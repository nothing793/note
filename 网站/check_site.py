#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验构建出来的站点：链接、锚点、图片是否都指得到真实目标。

笔记里共有 480 余条 `其他笔记.md#小节` 链接、470 余条同文件小节锚点与 80 余张配图，
它们在 GitHub / VS Code 预览里都能点通；搬到网站后是否还点得通，靠本脚本一条条核对。

四项检查：
  1. **标题锚点一致性**：每篇笔记的每个标题，按仓库自带的规则
     （`ADS/assets/check_md_anchors.py` 的 `slug()`）算出的锚点，必须真的出现在
     生成页面的 `id` 属性里 —— 这条能立刻发现「站点用的锚点算法和笔记不一致」；
  2. **源文件链接**：逐条解析 `.docs/**/*.md` 里的链接，`.md#小节` 要指得到目标页面
     的对应小节，图片等相对文件要真的被复制进了站点；
  3. **生成页面链接**：扫描 `site/**/*.html` 里所有 `href` / `src`，本地目标必须存在，
     且不应残留未改写的 `.md`；
  4. **站点资源**：MathJax 等 `extra_javascript` 资源是否存在。

完整报告写入 `网站/.cache/check_report.txt`（UTF-8）；控制台只打印摘要与问题行。

用法：python 网站/check_site.py
退出码：0 = 全部通过；1 = 有问题。
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = HERE / ".docs"
SITE = HERE / "site"
CACHE = HERE / ".cache"
CONFIG = HERE / "mkdocs.yml"
REPORT = CACHE / "check_report.txt"

SITE_URL_RE = re.compile(r"^site_url:\s*(\S+)\s*$", re.M)

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
LNK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ATTR_RE = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
ID_RE = re.compile(r'\sid="([^"]*)"')


def load_repo_slug():
    """加载仓库自带的锚点规则（`ADS/assets/check_md_anchors.py`），作为唯一标准。"""
    path = ROOT / "ADS" / "assets" / "check_md_anchors.py"
    if not path.is_file():
        sys.exit(f"找不到锚点规则脚本：{path}")
    spec = importlib.util.spec_from_file_location("repo_check_md_anchors", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def site_root_path() -> str:
    """`site_url` 里的部署路径（如 `/note/`）。

    设置了 `site_url` 后，主题资源与 `404.html` 会用**根绝对地址**（`/note/assets/...`），
    所以校验这些链接时要先把这段前缀去掉再落到 `site/` 上；前缀对不上说明
    「构建时的 site_url」与「实际部署位置」不一致，那正是需要报出来的问题。
    """
    m = SITE_URL_RE.search(CONFIG.read_text(encoding="utf-8"))
    return urlsplit(m.group(1)).path if m else ""


def strip_code(text: str) -> str:
    """屏蔽围栏代码块与行内代码，避免把代码里的方括号当链接。"""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub(" ", line))
    return "\n".join(out)


def page_of(md: Path) -> Path:
    """`.docs/a/b/c.md` → `site/a/b/c/index.html`；`index.md` → `site/index.html`。"""
    rel = md.relative_to(DOCS).with_suffix("")
    if rel.name == "index":
        return SITE / rel.parent / "index.html"
    return SITE / rel / "index.html"


def ids_of(html: Path) -> set[str]:
    if not html.is_file():
        return set()
    return set(ID_RE.findall(html.read_text(encoding="utf-8", errors="replace")))


def local_targets(text: str):
    """产出 (行号, 目标, 是否图片)。"""
    for no, line in enumerate(text.splitlines(), 1):
        for m in IMG_RE.finditer(line):
            yield no, m.group(1), True
        for m in LNK_RE.finditer(line):
            yield no, m.group(1), False


def main() -> int:
    repo = load_repo_slug()
    if not SITE.is_dir():
        sys.exit(f"还没有构建结果：{SITE}（先运行 python 网站/build.py）")

    problems: list[str] = []
    stats = {"pages": 0, "md_links": 0, "anchors": 0, "files": 0, "headings": 0}
    id_cache: dict[Path, set[str]] = {}

    def ids(html: Path) -> set[str]:
        if html not in id_cache:
            id_cache[html] = ids_of(html)
        return id_cache[html]

    for md in sorted(DOCS.rglob("*.md")):
        rel = md.relative_to(DOCS)
        html = page_of(md)
        stats["pages"] += 1
        if not html.is_file():
            problems.append(f"{rel}: 没有生成对应页面 {html.relative_to(SITE)}")
            continue

        # 1) 标题锚点一致性
        expected = repo.anchors_of(md)
        stats["headings"] += len(expected)
        missing = expected - ids(html)
        for anchor in sorted(missing):
            problems.append(f"{rel}: 页面里缺少标题锚点 #{anchor}（与仓库锚点规则不一致）")

        # 2) 源文件里的链接
        text = strip_code(md.read_text(encoding="utf-8", errors="replace"))
        for no, raw, is_img in local_targets(text):
            target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
            target = unquote(target)
            if not target or SCHEME_RE.match(target):
                continue
            path_part, _, frag = target.partition("#")
            if not path_part:
                stats["anchors"] += 1
                if frag and frag not in ids(html):
                    problems.append(f"{rel}:{no}: 同页锚点 #{frag} 指不到对应标题")
                continue
            target_path = (md.parent / path_part).resolve()
            if not target_path.exists():
                problems.append(f"{rel}:{no}: 源文件里链接的目标不存在：{target}")
                continue
            if is_img or target_path.suffix != ".md":
                stats["files"] += 1
                site_file = SITE / target_path.relative_to(DOCS)
                if not site_file.is_file():
                    problems.append(f"{rel}:{no}: 站点里缺少文件 {target}")
                continue
            stats["md_links"] += 1
            if DOCS not in target_path.parents and target_path != DOCS:
                problems.append(f"{rel}:{no}: 链接指到了 .docs/ 之外：{target}")
                continue
            target_html = page_of(target_path)
            if not target_html.is_file():
                problems.append(f"{rel}:{no}: 目标笔记没有生成页面：{target}")
                continue
            if frag and frag not in ids(target_html):
                problems.append(
                    f"{rel}:{no}: {path_part} 里没有小节锚点 #{frag}"
                )

    # 3) 生成页面里的链接
    root_path = site_root_path()
    for html in sorted(SITE.rglob("*.html")):
        if "assets" in html.relative_to(SITE).parts:
            continue
        body = html.read_text(encoding="utf-8", errors="replace")
        for raw in ATTR_RE.findall(body):
            target = unquote(raw.strip())
            if not target or target.startswith(("#", "data:", "mailto:")) or SCHEME_RE.match(target):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            if path_part.endswith(".md"):
                problems.append(
                    f"{html.relative_to(SITE)}: 残留未改写的 Markdown 链接 {target}"
                )
                continue
            if path_part.startswith("/"):
                # 主题资源与 404.html 用的是根绝对地址，需先去掉 site_url 的部署路径
                if root_path and path_part.startswith(root_path):
                    local = SITE / path_part[len(root_path):]
                elif root_path.rstrip("/") == path_part:
                    local = SITE
                else:
                    problems.append(
                        f"{html.relative_to(SITE)}: 绝对地址与 site_url 的部署路径"
                        f"（{root_path}）不一致：{target}"
                    )
                    continue
            else:
                local = html.parent / path_part
            if not local.exists():
                problems.append(f"{html.relative_to(SITE)}: 站内链接指不到文件 {target}")

    # 4) 站点资源
    for asset in ("assets/mathjax-config.js", "assets/vendor/mathjax/es5/tex-chtml.js"):
        if not (SITE / asset).is_file():
            problems.append(f"缺少站点资源 {asset}")

    lines = [
        "站点自检报告",
        f"页面 {stats['pages']} 个 · 跨文件链接 {stats['md_links']} 条 · "
        f"同页锚点 {stats['anchors']} 条 · 图片/附件 {stats['files']} 条 · "
        f"标题锚点 {stats['headings']} 个",
        "",
    ]
    if problems:
        lines.append(f"发现 {len(problems)} 个问题：")
        lines += [f"  - {p}" for p in problems]
    else:
        lines.append("结果：全部通过 ✓")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"自检：页面 {stats['pages']} · 跨文件链接 {stats['md_links']} · "
        f"同页锚点 {stats['anchors']} · 图片/附件 {stats['files']} · "
        f"标题锚点 {stats['headings']}"
    )
    if problems:
        print(f"✗ 发现 {len(problems)} 个问题（完整清单：{REPORT}）")
        for p in problems[:20]:
            print("   -", p)
        if len(problems) > 20:
            print(f"   …另有 {len(problems) - 20} 条，见报告文件")
        return 1
    print("✓ 全部链接、锚点、图片均正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())

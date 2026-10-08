#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 链接自检脚本（link checker）。

用途：扫描指定目录下的所有 `.md`，把里面用到的**相对路径（relative path）**
引用（图片 `![](...)`、普通链接 `[](...)`、引用式链接 `[label]: ...`）
按「该 md 文件所在目录」解析一遍，报告打不开的路径。

为什么需要它：md 里的相对路径是相对**当前文件所在目录**的，一旦笔记被移动、
改名或拆目录，图片就会静默失效（预览里只显示一个破图标），而失效原因往往
很难人工逐条排查。有了这个脚本，搬家后跑一遍即可发现全部断链。

顺带检查一条本项目规则（见 `学习/AGENTS.md` §2.7）：md 中**禁止使用绝对路径**
（`/mnt/c/...`、`C:\\...`），发现即报出。

用法：
    python3 check_md_links.py                 # 默认扫描本仓库根目录（学习/）
    python3 check_md_links.py ADS             # 只扫某个子目录（可给多个）
    python3 check_md_links.py --quiet .       # 只打印有问题的文件
    python3 check_md_links.py -x '大物实验/模板/*' ../..

预期报警（不是脚本出错）：
  - 模板文件（如 `大物实验/模板/实验报告模板.md`）里的示意图片引用；
  - 尚未拍摄/尚未放入 `assets/` 的照片（原始数据草稿纸、实验过程图）——
    按规则这些位置在拿到照片前应留 `<!-- -->` 占位，不该写 `![](...)`，
    所以报出来正好提醒去补照片或改成占位注释。

说明与已知限制：
  - 跳过隐藏目录（`.git`、`.codex` 等）、`__pycache__` 与围栏代码块（fenced
    code block）内的内容；行内代码 `` `...` `` 也先屏蔽，避免误报。
  - 外部链接（`http://`、`https://`、`mailto:` 等）不联网检查，只计数。
  - 带通配符的路径（如 `assets/fig_*.png`）按 glob 展开，一个都没匹配到才报错。
  - 只做「文件是否存在」的检查，不检查 anchor（`#小节`）是否真的存在。
退出码：0 = 全部通过；1 = 存在断链或绝对路径。
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SKIP_DIRS = {"__pycache__", "node_modules", "venv", ".venv"}
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
WIN_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
# ![...](target "title") / [...](target 'title')
IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
LNK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
REF_USE_RE = re.compile(r"!?\[[^\]]*\]\[([^\]]*)\]")
REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)")


def iter_md_files(root: Path, excludes: list[str]):
    """遍历 root 下的 .md；excludes 里的 glob（相对 root）会被跳过。"""
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts):
            continue
        if any(rel.match(pat) for pat in excludes):
            continue
        yield p


def split_fragment(target: str) -> tuple[str, str]:
    """把 `path#anchor` 拆成 (path, anchor)。"""
    if "#" in target:
        path, _, frag = target.partition("#")
        return path, frag
    return target, ""


def check_target(md: Path, target: str, root: Path) -> str | None:
    """返回问题描述；None 表示没问题。"""
    raw = target.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    raw = unquote(raw)
    if not raw or raw.startswith("#"):
        return None
    if raw.startswith("{") or raw.startswith("data:"):        # 模板变量 / 内嵌数据
        return None
    if SCHEME_RE.match(raw) and not WIN_ABS_RE.match(raw):    # 外部链接（http、mailto…）
        return None
    if WIN_ABS_RE.match(raw) or raw.startswith("/") or raw.startswith("\\\\"):
        return f"绝对路径（本项目禁止）: {raw}"
    path_part, _ = split_fragment(raw)
    if not path_part:
        return None
    if "*" in path_part or "?" in path_part:                  # 通配写法
        base = (md.parent / path_part).as_posix()
        return None if glob.glob(base) else f"无匹配文件: {raw}"
    cand = md.parent / path_part
    if cand.exists():
        return None
    # 兜底：Windows 上大小写不敏感，改名后可能出现大小写不一致
    parent = cand.parent
    if parent.is_dir() and any(f.name.lower() == cand.name.lower() for f in parent.iterdir()):
        return f"大小写不一致: {raw}"
    return f"缺失: {raw}"


def scan(md: Path, root: Path):
    issues: list[tuple[int, str]] = []
    external = 0
    checked = 0
    refdefs: dict[str, str] = {}
    lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    in_fence = False
    for no, raw_line in enumerate(lines, 1):
        if FENCE_RE.match(raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), raw_line)
        for m in REF_DEF_RE.finditer(line):
            if not m.group(1).startswith("^"):                # 跳过脚注
                refdefs[m.group(1).strip().lower()] = m.group(2)
        targets = [m.group(1) for m in IMG_RE.finditer(line)]
        targets += [m.group(1) for m in LNK_RE.finditer(line)]
        for m in REF_USE_RE.finditer(line):
            key = m.group(1).strip().lower()
            if key in refdefs:
                targets.append(refdefs[key])
        for t in targets:
            if SCHEME_RE.match(t) and not WIN_ABS_RE.match(t):
                external += 1
                continue
            checked += 1
            problem = check_target(md, t, root)
            if problem:
                issues.append((no, problem))
    return issues, checked, external


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Markdown 相对路径引用自检（link checker）")
    ap.add_argument("roots", nargs="*", help="要扫描的目录（默认：本仓库根目录 学习/）")
    ap.add_argument("--quiet", "-q", action="store_true", help="只打印有问题的文件")
    ap.add_argument("--exclude", "-x", action="append", default=[],
                    metavar="GLOB", help="跳过匹配的文件（相对根的 glob，可重复，"
                                         "例：-x '大物实验/模板/*'）")
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]        # …/学习
    roots = [Path(r).resolve() for r in args.roots] or [repo_root]

    total_files = total_checked = total_external = 0
    bad_files = 0
    for root in roots:
        print(f"扫描: {root}")
        for md in iter_md_files(root, args.exclude):
            total_files += 1
            issues, checked, external = scan(md, root)
            total_checked += checked
            total_external += external
            if issues:
                bad_files += 1
                print(f"\n{md.relative_to(root) if root in md.parents else md}")
                for no, problem in issues:
                    print(f"  第 {no} 行  {problem}")
            elif not args.quiet:
                print(f"  ok  {md.relative_to(root)}（{checked} 条本地引用）")

    print("\n" + "-" * 56)
    print(f"扫描 {total_files} 个 md 文件，检查 {total_checked} 条本地路径引用"
          f"（另有 {total_external} 条外部链接未联网检查）")
    if bad_files:
        print(f"结果：{bad_files} 个文件存在断链或绝对路径，需要修")
        return 1
    print("结果：全部通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())

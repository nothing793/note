#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 锚点自检脚本（anchor checker）——配合 `check_md_links.py` 使用。

`check_md_links.py` 只检查「相对路径」能不能打开，不管 `#小节` 是否存在；
本脚本专门检查 md 里的**标题锚点链接**（`[文字](#锚点)`、`[文字](其他笔记.md#锚点)`）
是否真的指得到对应标题，顺便报出「用了锚点但目标文件里没有该标题」的情况。

锚点规则按 GitHub / VS Code 预览的通用做法（与 `sys2/笔记/*.md` 现有写法一致）：

  1. 去掉 `#`、`*`、`` ` `` 等标记，转小写；
  2. 去掉标点（全角、半角都去，含 `（）【】：，.。/` 与破折号），保留中英文、数字、下划线；
  3. 空格 → `-`（多个连续空格 → 多个 `-`）；
  4. 同名标题按出现顺序加 `-1`、`-2`。

用法：
    python3 check_md_anchors.py            # 扫描本仓库（学习/）下所有 md
    python3 check_md_anchors.py ADS        # 只扫某个子目录（可给多个）
    python3 check_md_anchors.py --quiet .  # 只打印有问题的文件

退出码：0 = 全部通过；1 = 存在指不到的锚点。
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

SKIP_DIRS = {"__pycache__", "node_modules", "venv", ".venv"}
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`+[^`]*`+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# [文字](target "title")
LNK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
def slug(title: str) -> str:
    """GitHub / VS Code 预览风格的标题锚点。

    保留：Unicode 字母 / 数字 / 组合记号、下划线、空格与 ASCII 连字符 `-`；
    其余字符（`（）【】：、。，.·—–/` 引号、`$`、`%` 等）一律去掉；空格换成 `-`。
    """
    t = title.strip().lower().replace("*", "").replace("`", "")
    kept = []
    for ch in t:
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "N", "M") or ch in {" ", "-", "_"}:
            kept.append(ch)
    return "".join(kept).replace(" ", "-")


def anchors_of(md: Path) -> set[str]:
    """算出某个 md 里所有标题的锚点（含 GitHub 风格的 -1 / -2 去重后缀）。"""
    heads: list[str] = []
    in_fence = False
    for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            heads.append(m.group(2))
    seen: dict[str, int] = {}
    out: set[str] = set()
    for h in heads:
        a = slug(h)
        n = seen.get(a, 0)
        seen[a] = n + 1
        out.add(a if n == 0 else f"{a}-{n}")
    return out


def strip_code(text: str) -> str:
    """把行内代码与围栏代码块屏蔽掉，避免误报。"""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub(" ", line))
    return "\n".join(out)


def iter_md_files(root: Path, excludes: list[str]):
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts):
            continue
        if any(rel.match(pat) for pat in excludes):
            continue
        yield p


def main() -> int:
    ap = argparse.ArgumentParser(description="检查 md 里的标题锚点链接是否有效")
    ap.add_argument("roots", nargs="*", default=["."], help="要扫描的目录（默认当前目录）")
    ap.add_argument("-x", "--exclude", action="append", default=[], help="要跳过的文件 glob（可多次）")
    ap.add_argument("--quiet", action="store_true", help="只打印有问题的文件")
    args = ap.parse_args()

    bad_total = links_total = 0
    for root_arg in args.roots:
        root = Path(root_arg).resolve()
        cache: dict[Path, set[str]] = {}
        n_md = n_links = n_bad = 0
        for md in iter_md_files(root, args.exclude):
            n_md += 1
            text = strip_code(md.read_text(encoding="utf-8", errors="replace"))
            problems = []
            file_links = 0
            for target in (unquote(t[1:-1]) if t.startswith("<") else unquote(t) for t in LNK_RE.findall(text)):
                if "#" not in target:
                    continue
                path_part, _, frag = target.partition("#")
                if not frag:
                    continue
                n_links += 1
                file_links += 1
                if path_part == "":                      # 同文件内的锚点
                    tgt_file, shown = md, f"#{frag}"
                else:
                    tgt_file = (md.parent / path_part).resolve()
                    shown = f"{path_part}#{frag}"
                    if not tgt_file.exists():
                        problems.append(f"{shown}（文件不存在：{tgt_file}）")
                        continue
                if tgt_file not in cache:
                    cache[tgt_file] = anchors_of(tgt_file)
                if frag not in cache[tgt_file]:
                    problems.append(f"{shown}（{tgt_file.name} 里没有这个标题锚点）")
            if problems:
                n_bad += len(problems)
                print(f"✗ {md.relative_to(root) if md.is_relative_to(root) else md}")
                for p in problems:
                    print(f"    {p}")
            elif not args.quiet:
                print(f"  ok  {md.relative_to(root) if md.is_relative_to(root) else md}（{file_links} 条锚点链接）")
        print("-" * 56)
        print(f"{root_arg}：扫描 {n_md} 个 md，检查 {n_links} 条锚点链接，问题 {n_bad} 条")
        links_total += n_links
        bad_total += n_bad
    print(f"合计：{links_total} 条锚点链接，{bad_total} 条问题" + ("（全部通过 ✓）" if bad_total == 0 else ""))
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())

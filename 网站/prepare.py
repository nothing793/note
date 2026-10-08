#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把三门课的笔记汇集到 `网站/.docs/`（MkDocs 的 `docs_dir`），供 `mkdocs build` 使用。

为什么需要这一步：笔记的「家」在仓库里各自的 `笔记/` 目录（`ADS/笔记`、
`密码学基础/笔记`、`sys2/笔记`），但 MkDocs 要求所有页面都在 `docs_dir` 里面。
本脚本**只做复制、不改动任何原始文件**，并保持相对目录结构不变，
这样笔记里 480 余条 `../其他笔记.md#小节`、`assets/*.png` 之类的相对链接
在站点里依旧成立（MkDocs 随后会把 `.md` 改写成对应的网页地址）。

每次运行都会先**清空 `网站/.docs/`**，所以不要直接改 `.docs/` 里的文件——
要改就改 `ADS/笔记/`、`密码学基础/笔记/`、`sys2/笔记/` 里的原件。

目录名用点号开头（`.docs`）是有意的：仓库自带的两个自检脚本
（`ADS/assets/check_md_links.py`、`check_md_anchors.py`）会跳过 `.` 开头的目录，
不会把生成出来的副本当成笔记重复检查，命令行也就无需额外传 `-x`。

用法：python 网站/prepare.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # 仓库根目录（学习/）
DOCS = HERE / ".docs"

COURSES = ["ADS", "密码学基础", "sys2"]
SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
SKIP_FILES = {"tasks.md"}               # 个人待办草稿，不作为笔记发布

# 复制关系：(源, 目标) —— 目标都相对 .docs/
#
# 站点首页的正文放在仓库根目录的 `网站首页.md`：这样它里面的相对链接
# （`ADS/笔记/00_索引.md` 等）在仓库根目录与 `网站/.docs/` 下都成立，
# 仓库自带的两个自检脚本、VS Code 预览与站点构建因此保持一致。
STAGED_FILES = [
    (ROOT / "README.md", DOCS / "关于仓库.md"),
    (ROOT / "网站首页.md", DOCS / "index.md"),
]


def copy_notes(counts: dict[str, int]) -> None:
    """复制三门课的 `笔记/*.md` 与 `笔记/assets/**`（跳过缓存与草稿）。"""
    for course in COURSES:
        src_dir = ROOT / course / "笔记"
        if not src_dir.is_dir():
            print(f"警告：找不到 {src_dir}", file=sys.stderr)
            continue
        dst_dir = DOCS / course / "笔记"
        for src in sorted(src_dir.rglob("*")):
            rel = src.relative_to(src_dir)
            if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
                continue
            if src.is_dir():
                continue
            if src.suffix in SKIP_SUFFIXES:
                continue
            if src.parent == src_dir and src.name in SKIP_FILES:
                continue
            if src.parent == src_dir and src.suffix != ".md":
                continue                   # 笔记目录根下只发布 Markdown
            dst = dst_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            counts["笔记" if src.suffix == ".md" else "附件"] += 1


def copy_tree(src: Path, dst: Path, counts: dict[str, int], what: str) -> None:
    if not src.is_dir():
        print(f"警告：找不到 {src}（先跑 网站/fetch_mathjax.py？）", file=sys.stderr)
        return
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if item.is_dir():
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        counts[what] += 1


def main() -> int:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    counts = {"笔记": 0, "附件": 0, "站点资源": 0, "MathJax": 0}

    copy_notes(counts)

    for src, dst in STAGED_FILES:
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            counts["笔记"] += 1
        else:
            print(f"警告：找不到 {src}", file=sys.stderr)

    copy_tree(HERE / "static", DOCS / "assets", counts, "站点资源")
    copy_tree(HERE / "vendor" / "mathjax" / "es5", DOCS / "assets" / "vendor" / "mathjax" / "es5", counts, "MathJax")

    print("已汇集到", DOCS)
    for k, v in counts.items():
        print(f"  {k}: {v} 个文件")
    if counts["MathJax"] == 0:
        print("提示：MathJax 尚未下载，公式将无法显示 —— 先运行 python 网站/fetch_mathjax.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

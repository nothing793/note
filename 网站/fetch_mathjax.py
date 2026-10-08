#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 MathJax 的浏览器端文件下载到 `vendor/mathjax/`（本地打包，离线可用）。

只取渲染所需的最小集合：
  - `es5/tex-chtml.js`：TeX 输入 + CHTML 输出的合并包（自包含，不含字体）；
  - `es5/output/chtml/fonts/woff-v2/*.woff`：CHTML 输出用的 Web 字体。

目录结构与 npm 包保持一致，MathJax 才会按相对路径找到字体。
已存在的文件会跳过，可反复运行。

用法：python 网站/fetch_mathjax.py
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

VERSION = "3.2.2"
VENDOR = Path(__file__).resolve().parent / "vendor" / "mathjax"
BASE = f"https://cdn.jsdelivr.net/npm/mathjax@{VERSION}/"
FONT_DIR = "es5/output/chtml/fonts/woff-v2/"
WANTED = {"es5/tex-chtml.js"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "note-site-builder"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    listing = json.loads(
        fetch(f"https://data.jsdelivr.com/v1/packages/npm/mathjax@{VERSION}?structure=flat")
    )["files"]
    paths = [f["name"].lstrip("/") for f in listing]
    targets = sorted(
        p for p in paths if p in WANTED or (p.startswith(FONT_DIR) and p.endswith(".woff"))
    )
    if not any(p in WANTED for p in targets):
        print("错误：文件清单里找不到 es5/tex-chtml.js", file=sys.stderr)
        return 1

    downloaded = skipped = 0
    for rel in targets:
        dest = VENDOR / rel
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(fetch(BASE + rel))
        downloaded += 1
    print(f"MathJax {VERSION}: 下载 {downloaded} 个文件，跳过已存在 {skipped} 个")
    print(f"目标目录：{VENDOR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

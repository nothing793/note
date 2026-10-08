#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub / VS Code 预览风格的标题锚点（slug），供 `mkdocs.yml` 里的 `toc.slugify` 使用。

为什么必须自己写一份：MkDocs 默认用 python-markdown 的 `slugify_unicode`，它与
GitHub 的算法有三处不同——

| 情况 | GitHub（本仓库笔记在用） | python-markdown 默认 |
|---|---|---|
| 标题里的标点 | 直接删掉，空格各自变 `-` | 先做 NFKC 归一化再删，**连续空格 / 连字符并成一个 `-`** |
| 首尾空格、`-` | 保留（空格仍各变一个 `-`） | `strip()` 掉 |
| 同名标题 | 追加 `-1`、`-2` | 追加 `_1`、`_2` |

例子：`### 6.1 关联知识点（跨讲 / 跨资料）`
  - GitHub → `61-关联知识点跨讲--跨资料`（`/` 两侧的空格各留一个 `-`）
  - 默认 → `61-关联知识点跨讲-跨资料`（被并成一个 `-`）

本仓库 `ADS/笔记`、`密码学基础/笔记`、`sys2/笔记` 里共 480 余条
`其他笔记.md#小节` 链接，锚点全部按 GitHub 规则写的，也用
`ADS/assets/check_md_anchors.py` 自检；所以这里复刻 GitHub 的算法，
保证「Markdown 里点得通」与「网站上点得通」完全一致。

导入本模块时会顺带把 python-markdown 的重名后缀从 `_1` 改成 `-1`
（见 `_install_github_unique`），这样两类锚点规则在第三种情况下也一致。
"""
from __future__ import annotations

import re
import unicodedata

# 除 Unicode 字母 / 数字 / 组合记号外，额外保留的字符
_EXTRA_KEEP = frozenset(" -_")


def slugify(value: str, separator: str = "-") -> str:
    """把标题文本转成 GitHub 风格的锚点（与 `check_md_anchors.py` 的 `slug()` 等价）。

    保留：字母 / 数字 / 组合记号（含中文）、下划线、空格与 ASCII 连字符；
    其余（全角半角标点、`$`、`%`、emoji 等）一律删除；空格逐个换成 `separator`。
    """
    text = value.strip().lower().replace("*", "").replace("`", "")
    kept = [
        ch
        for ch in text
        if unicodedata.category(ch)[0] in ("L", "N", "M") or ch in _EXTRA_KEEP
    ]
    return "".join(kept).replace(" ", separator)


_DUP_RE = re.compile(r"^(.*)-([0-9]+)$")


def unique_github(anchor: str, used: set) -> str:
    """重名时追加 `-1`、`-2`…（GitHub 的规则），替代 python-markdown 的 `_1`。"""
    while anchor in used or not anchor:
        m = _DUP_RE.match(anchor)
        anchor = f"{m.group(1)}-{int(m.group(2)) + 1}" if m else f"{anchor}-1"
    used.add(anchor)
    return anchor


def _install_github_unique() -> None:
    """让 python-markdown 的 toc 扩展改用 `unique_github`。

    toc 扩展在 `TocTreeprocessor.run()` 里按模块全局名调用 `unique()`，
    所以替换模块属性即可生效；只影响本进程（即本站点构建）。
    """
    from markdown.extensions import toc as _toc

    if getattr(_toc, "_github_unique_installed", False):
        return
    _toc.unique = unique_github
    _toc._github_unique_installed = True


_install_github_unique()

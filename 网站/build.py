#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建（并自检）笔记网站。

一条命令走完三步：
  1. `prepare.py`：把三门课的笔记与配图汇集到 `.docs/`；
  2. `mkdocs build`：生成静态站点到 `site/`；
  3. `check_site.py`：校验站点里每条链接都指得到真实页面 / 小节 / 图片。

用法：
    python 网站/build.py            # 构建 + 自检
    python 网站/build.py -s         # 本地预览（http://127.0.0.1:8000，Ctrl+C 退出）
    python 网站/build.py --no-check # 只构建，不跑自检

注意：`mkdocs.yml` 里用 `!!python/name:gh_slug.slugify` 指定标题锚点算法，
需要 `网站/` 在 `sys.path` 上，所以请用本脚本（或先 `cd 网站` 再跑 `mkdocs`），
不要从仓库根目录直接执行 `mkdocs build -f 网站/mkdocs.yml`。
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
CONFIG = HERE / "mkdocs.yml"
WARNINGS = CACHE / "build_warnings.txt"


class _WarningCollector(logging.Handler):
    """收集 MkDocs 的 WARNING 及以上日志（链接找不到之类的问题都走这里）。"""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(f"{record.levelname} {record.name}: {record.getMessage()}")


def run_prepare() -> None:
    import prepare

    if prepare.main() != 0:
        sys.exit("prepare.py 失败：请先运行 python 网站/fetch_mathjax.py")


def main() -> int:
    args = sys.argv[1:]
    # 让 mkdocs.yml 里的 !!python/name:gh_slug.slugify 能导入；
    # 同时把工作目录切到 网站/，使配置里的相对路径（.docs/、site/）按预期解析。
    sys.path.insert(0, str(HERE))
    os.chdir(HERE)
    CACHE.mkdir(exist_ok=True)

    if "-s" in args or "--serve" in args:
        from mkdocs.commands import serve

        print("本地预览：http://127.0.0.1:8000 （Ctrl+C 退出）")
        serve.serve(config_file=str(CONFIG), dev_addr="127.0.0.1:8000")
        return 0

    run_prepare()

    from mkdocs.commands.build import build
    from mkdocs.config import load_config

    collector = _WarningCollector()
    logging.getLogger("mkdocs").addHandler(collector)

    config = load_config(config_file=str(CONFIG))
    build(config)
    print(f"构建完成 → {config['site_dir']}")

    if collector.lines:
        WARNINGS.write_text("\n".join(collector.lines) + "\n", encoding="utf-8")
        print(f"⚠ MkDocs 警告 {len(collector.lines)} 条，详见 {WARNINGS}")
    else:
        WARNINGS.unlink(missing_ok=True)

    if "--no-check" in args:
        return 0

    import check_site

    return check_site.main()


if __name__ == "__main__":
    sys.exit(main())

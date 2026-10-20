# 计算机系统 II（sys2）

浙江大学《计算机系统 II》（Computer Systems II；第 1–4 讲讲义署卢立 Li Lu，第 5–6 讲 PDF 标题页署 Haifeng Liu）的讲义原件与整理笔记的工作目录。

## 目录用途

| 路径 | 用途 |
|---|---|
| `lec01-2026-chang.pdf`、`lec02(2).pdf`、`lec03-2026.pdf`、`lec04-2026.pdf`、`lec05-advanced pipeline.pdf`、`lec06-software-hardware-interface.pdf`、`lec05.pptx` | 课程讲义原件（**只读**：不改名、不移动、不修改，含 `lec02(2)` 的括号与 `lec05-advanced pipeline.pdf` 的空格）；第 5、6 讲以 PDF 为准，旧版 `lec05.pptx` 仅用于附录 A 的 Tomasulo 例题 |
| `笔记/` | 按讲次整理的 Markdown 笔记与讲义原页配图（发布到笔记网站） |

## 笔记约定

- `笔记/00_索引.md` 是入口：文件列表、一句话摘要、建议阅读顺序、配图清单与待确认事项；
- 每一讲一篇 `NN_第NN讲_<主题>.md`，结构固定：**本讲速览 → 按小节展开（带 PDF 页码）→ 听课重点与易混点 → 课前自测 → 来源、页码对照与待确认**；第 1–6 讲统一用 PDF 页码 `(p.x)`，只有第 5 讲附录 A 用旧版 PPTX 的 `(s.x)`；
- 配图统一放 `笔记/assets/`，命名 `fig_p<PDF 页码>_<主题>.png`，均为**讲义原页导出**（非自绘）；旧版第 5 讲的 `fig_s*.png` 作为历史配图保留。
- 标注约定：`【讲义】` 为幻灯片原文或直接提炼，`(p.x)` 指 **PDF 页码**，`待确认` 指讲义未写明或存在疑点之处；
- 讲义页面的小节号沿用讲义自身编号（第 1 讲 §1.x、第 2 讲 §2.x、第 3 讲 §3.x、第 4 讲 §4.x、第 5 讲 §5.x、第 6 讲 §6.x），与教材章节号可能不同；个别页脚残留旧编号，已在各篇待确认中列出。

## 修改笔记后

1. 同步 `笔记/00_索引.md`（文件列表、配图清单、待确认事项）；
2. 新增 / 改名 / 调整标题后，同步 `网站/mkdocs.yml` 的 `nav`；
3. 跑自检：`python3 ADS/assets/check_md_links.py sys2`、`python3 ADS/assets/check_md_anchors.py sys2`；
4. 重建站点：`python 网站/build.py`（细则见 `网站/README.md`）。

> 讲义原件（本目录下的 `*.pdf`）**不入库**，只提交 `笔记/` 下的整理成果与配图；规则见上级目录 `../AGENTS.md` 与根 `README.md`。

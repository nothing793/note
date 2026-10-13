# ADS（高级数据结构与算法分析）· 笔记（`ADS/笔记/`）

浙江大学「高级数据结构和算法分析」（主讲：陈昊）课前笔记的 **Markdown 原件**与配图。
本目录是笔记的「家」：改内容改这里的文件；站点构建时由 `网站/prepare.py` 复制到 `网站/.docs/`（**不要**直接改生成副本）。

## 目录内容

| 文件 | 主题 |
|---|---|
| `00_索引.md` | **入口**：文件列表、一句话摘要、建议阅读顺序、配图与脚本清单、待确认事项 |
| `01_ADS00_课程介绍与考核.md` | 课程介绍与考核方式 |
| `02_ADS001_伸展树与摊还分析.md` | 伸展树（splay tree）与摊还分析（amortized analysis，势能法 / 记账法） |
| `03_ADS02_红黑树与B+树.md` | 红黑树（red-black tree）与 B+ 树（B+ tree） |
| `04_ADS03_倒排文件索引.md` | 倒排文件索引（inverted file index，trie / 哈希表（hash table）） |
| `05_ADS04_左式堆与斜堆.md` | 左式堆（leftist heap）与斜堆（skew heap） |
| `06_ADS05_二项队列.md` | 二项队列（binomial queue） |
| `07_ADS06_回溯算法.md` | 回溯算法（backtracking，含 $\alpha$-$\beta$ 剪枝（alpha-beta pruning）） |
| `08_ADS07_分治法与递归式.md` | 分治法（divide and conquer）与递归式（recurrence）求解 |
| `09_ADS08_动态规划.md` | 动态规划（dynamic programming） |
| `10_ADS09_贪心算法.md` | 贪心算法（greedy algorithm）与 Huffman 编码（Huffman coding） |
| `11_ADS10_NP完全性.md` | NP 完全性（NP-completeness，归约（reduction）） |
| `12_ADS11_近似算法.md` | 近似算法（approximation algorithm） |
| `13_ADS12_局部搜索.md` | 局部搜索（local search）与模拟退火（simulated annealing） |
| `14_ADS13_随机化算法.md` | 随机化算法（randomized algorithm） |
| `15_ADS14_并行算法.md` | 并行算法（parallel algorithm）与并行模型（PRAM 等） |
| `16_ADS15_外部排序.md` | 外部排序（external sorting，多路归并 / 置换选择） |
| `tasks.md` | 个人待办草稿：**不发布**到站点（在 `网站/prepare.py` 的 `SKIP_FILES` 中） |
| `assets/` | 配图与生成脚本，见下 |

各篇的一句话摘要、建议阅读顺序与页码对照见 [`00_索引.md`](00_索引.md)。

## `assets/` 的约定

- `fig_*.png`：配图。既有**讲义原页导出**的图，也有**自绘**图（如 `fig_leftist_*`、`fig_skew_*` 由脚本生成）；
  自绘图在图注中均标明「自绘」；
- `make_*.py`：生成自绘配图的脚本（`make_avl_figs.py`、`make_splay_figs.py`、`make_amort_figs.py`、
  `make_leftist_skew_figs.py`、`make_ads02_figs.py`、`make_ads_notes_figs.py`、`make_ads05_figs.py`）——**入库**（`.gitignore` §10 白名单放行），
  笔记正文直接链接这些脚本，便于复现；
- 图一律用**相对路径**引用（`assets/fig_*.png`），不写绝对路径、不内嵌 base64。

## 本课特有的写作约定

1. **术语必须标英文**（硬性）：概念名词、计算机术语一律写成 `中文（English）`，规则与示例见 `../AGENTS.md` §1；
   每个文档内**首次出现**处标注即可，代码块、公式、讲义原话引用不标。
2. **主标准**：课件 `Materials/Student Slides/ADS*.ppt`（**只读、不入库**）＋ 站外主参考「ADS · 算法研习室」；
   课件勘误以研习室结论为准，写法是另起一条 `> 研习室勘误（p.x）：……`；正文内联提到该站写「（研习室）」，
   完整站名与 URL 只写在 `00_索引.md` 与 `../AGENTS.md`。
3. **每篇结构**：速览 → 核心概念 → 关键公式与算法 → 例子 → 听课重点与易混点 → 课前自测 / 课后回顾 → 来源；
   自测题的每条都带**本讲小节锚点**，篇末另设「关联知识点（跨讲 / 跨资料）」。

## 注意事项

- 课件与教材原件（`../Materials/`）**只读**：不改名、不移动、不修改；
- 新增 / 改名 / 调整标题后：同步 [`00_索引.md`](00_索引.md) → 同步 `网站/mkdocs.yml` 的 `nav` → 跑自检 → 重建站点；
- 交付前自检（脚本与本课程无关，放在 `../assets/`）：

  ```bash
  python3 ADS/assets/check_md_links.py ADS     # 相对路径能否打开
  python3 ADS/assets/check_md_anchors.py ADS   # 标题锚点能否指到
  python3 网站/build.py                        # 汇集 → 构建 → 站点自检
  ```

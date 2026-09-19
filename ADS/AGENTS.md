# AGENTS.md — ADS（高级数据结构与算法分析）笔记规则

> 适用范围：本文件位于 `ADS/`，对该目录及其所有子目录（`笔记/`、`assets/`、`Materials/`，其中 `笔记/assets/` 存放笔记配图与生成脚本）生效。
> 就地优先：本文件写到的内容优先于上级 `学习/AGENTS.md`；上级文件中未被本文件涉及的通用规则（不修改原始资料、不编造、汇报格式、文件命名等）继续适用。
> 最近更新：2026-09-16

## 1. 术语必须标注英文（硬性要求）

**概念名词、计算机术语一律在括号内备注英文原文，不能只挑“重点”的几个标。**

格式：`中文（English）`，用全角括号，紧跟术语之后：

- 平衡因子（balance factor）、内部路径长度（internal path length）
- 自调整二叉搜索树（self-adjusting binary search tree）、访问局部性（locality of reference）
- 势能法（potential method）、摊还代价（amortized cost）、望远镜求和（telescoping sum）
- 中序遍历（inorder traversal）、叶子结点（leaf）、双旋（double rotation）

要覆盖的类别（都属于“术语”，逐类都要标）：

| 类别 | 例子 |
|---|---|
| 数据结构与抽象数据类型 | 节点（node）、根节点（root）、子树（subtree）、叶节点（leaf）、指针（pointer）、链表（linked list）、栈（stack）、队列（queue）、哈希表（hash table） |
| 算法与设计范式 | 分治法（divide and conquer）、动态规划（dynamic programming）、贪心算法（greedy algorithm）、回溯（backtracking）、近似算法（approximation algorithm）、随机化算法（randomized algorithm） |
| 操作与性质 | 插入（insertion）、删除（deletion）、查找（search）、旋转（rotation）、平衡条件（balance condition）、高度（height）、深度（depth）、路径（path）、祖先（ancestor） |
| 分析与复杂度术语 | 最坏情况（worst case）、平均情况（average case）、摊还分析（amortized analysis）、势能（potential）、秩（rank）、递推式（recurrence）、下界（lower bound）、渐进记号（asymptotic notation） |
| 通用计算机术语 | 缓存（cache）、索引（index）、并行（parallelism）、虚存（virtual memory）、编码（encoding） |

细则：

1. **位置**：每个文档、或每个 `#` 大节内，一个术语**首次出现时标注**即可；同一文档里重复出现不必反复标。标题、正文、列表、表格表头、图题与图注都算正文。
2. **方向**：中文在前写 `中文（English）`；本来就是英文或缩写的写法（`splay tree`、`AVL`、`BST`、`NP-hard`、`zig-zig`）不必翻成中文，必要时补中文，如 `splay tree（伸展树）`。同一文档内风格保持一致。
3. **不标注的地方**：代码块与命令行、文件路径、讲义原文引用（`*...*` 内的英文原话）、公式与变量符号（$X$、$P$、$bf$、$R(i)$ 等）。标注英文不得改动公式、图片、编号等既有内容。
4. **与上级规则的关系**：上级 `学习/AGENTS.md` 0.2 第 1 条要求“中文为默认输出语言、英文术语保持原样”；本条只要求给中文术语**补上英文**，两者不冲突。
5. **自检**：交付前用 `grep -o "（[A-Za-z][^）]*）" 文件.md | wc -l` 大致自查标注数量，再通读一遍看是否漏掉了明显该标的概念名词。

## 2. 落实情况

| 文件 / 目录 | 状态 |
|---|---|
| `笔记/02_ADS001_伸展树与摊还分析.md`（原 `ADS/AVL和splay.md`，2026-09-19 移入 `笔记/`） | 已按本规则逐节标注（2026-09-16，44 处） |
| `笔记/*.md`（17 个文件） | 已按本规则逐文件标注（2026-09-16，共 452 处；每个术语只标首次出现） |
| 之后新建或改写的 ADS 笔记 | 一律按第 1 条执行 |

> 标注办法：逐文件扫描概念名词 → 每个术语在**该文件内首次出现**处补 `（English）`；已经是英文/缩写或用「英文（中文）」写法的（如 `splay tree（伸展树）`、`有序段（run）`）不动；代码块、行内/独立公式、讲义原话引用与 `> 来源` 等元信息行不标注。

# -*- coding: utf-8 -*-
"""ADS05 二项队列（binomial queue）的自绘示意图。
图均以英文标注（避免中文字体缺失的方框），中文说明写在笔记的图注里。
运行：python3 make_ads05_figs.py   （图片写在脚本所在目录）

- fig_binomial_insert7.png   ：依次插入 1..7 后队列（森林）的样子
- fig_binomial_deletemin.png ：DeleteMin 的四步（只画结构，不写键值）

两张图里的树都由脚本**真实跑**讲义/教材的二项队列算法得到（BinQueue / combine_trees）：
进位规则、以及 CombineTrees "头插 ⇒ 孩子按规模递减" 都照讲义代码做，不是手画的示意。
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["axes.unicode_minus"] = False


# ----------------------------------------------------------------- 二项队列算法
class Node:
    def __init__(self, key):
        self.key = key
        self.children = []          # children[0] 是**最大**的子树（按规模递减）
        self.x = 0.0
        self.y = 0.0


def combine_trees(t1, t2):
    """讲义 CombineTrees：大根整棵挂到小根孩子链的最前面（头插）。"""
    if t1.key > t2.key:
        return combine_trees(t2, t1)
    t1.children.insert(0, t2)
    return t1


class BinQueue:
    """`TheTrees[]` 的等价物：dict，rank -> 该阶那棵树的根。"""

    def __init__(self):
        self.trees = {}

    def _highest(self):
        return max(self.trees) if self.trees else -1

    def merge(self, other):
        """按阶逐位做二进制加法（讲义 Merge 的 8 个分支），高位没有树时早停。"""
        carry, out = None, {}
        top = max(self._highest(), other._highest())
        i = 0
        while i <= top or carry is not None:
            t1 = self.trees.get(i)
            t2 = other.trees.get(i)
            case = (4 if carry else 0) + (2 if t2 else 0) + (1 if t1 else 0)
            if case in (0, 1):
                if t1 is not None:
                    out[i] = t1
            elif case == 2:
                out[i] = t2
            elif case == 4:
                out[i] = carry
                carry = None
            elif case == 3:
                carry = combine_trees(t1, t2)
            elif case == 5:
                carry = combine_trees(t1, carry)
            elif case == 6:
                carry = combine_trees(t2, carry)
            else:                                   # case == 7
                out[i] = carry
                carry = combine_trees(t1, t2)
            i += 1
        self.trees = out
        return self

    def insert(self, key):
        one = BinQueue()
        one.trees[0] = Node(key)
        return self.merge(one)

    def size(self):
        return sum(2 ** r for r in self.trees)

    def forest(self):
        """按阶升序返回 [(rank, root), ...]。"""
        return [(r, self.trees[r]) for r in sorted(self.trees)]


def clone(node):
    """深拷贝一棵树：每个快照要独立的结构，否则后面的插入会改掉前面画的树。"""
    new = Node(node.key)
    new.children = [clone(c) for c in node.children]
    return new


# --------------------------------------------------------------------- 画树工具
def layout(node, depth=0, slot=None):
    """经典树布局：叶子从左到右占槽位，父亲居中；y = -depth（根在上）。"""
    slot = [0] if slot is None else slot
    node.y = -depth
    if not node.children:
        node.x = float(slot[0])
        slot[0] += 1
    else:
        xs = []
        for c in node.children:
            layout(c, depth + 1, slot)
            xs.append(c.x)
        node.x = (min(xs) + max(xs)) / 2.0
    return node


def nodes_of(node):
    out = [node]
    for c in node.children:
        out += nodes_of(c)
    return out


def draw_forest(ax, forest, labels=None, node_label=None, pt_size=300, fs=8, gap=1.6):
    """forest: [(rank, root), ...]；labels: 每棵树下方的小标签（如 '$B_3$'）。"""
    x_off, max_depth = 0.0, 0
    trees = []
    for rank, root in forest:
        layout(root)
        ns = nodes_of(root)
        span = max(n.x for n in ns) - min(n.x for n in ns)
        trees.append((ns, min(n.x for n in ns), x_off))
        max_depth = max(max_depth, max(-n.y for n in ns))
        x_off += span + gap
    right = x_off - gap
    for idx, (ns, x_min, off) in enumerate(trees):
        for n in ns:
            for c in n.children:
                ax.plot([off + n.x - x_min, off + c.x - x_min], [n.y, c.y],
                        color="#444444", lw=1.1, zorder=1, solid_capstyle="round")
            ax.scatter([off + n.x - x_min], [n.y], s=pt_size, facecolor="white",
                       edgecolor="#333333", linewidths=1.1, zorder=2)
            if node_label is not None:
                ax.text(off + n.x - x_min, n.y, node_label(n), ha="center", va="center",
                        fontsize=fs, zorder=3)
        if labels is not None:
            xs = [off + n.x - x_min for n in ns]
            ax.text((min(xs) + max(xs)) / 2.0, -max_depth - 0.55, labels[idx],
                    ha="center", va="top", fontsize=fs + 1, color="#b03030")
    ax.set_xlim(-0.7, right + 0.7)
    ax.set_ylim(-max_depth - 1.25, 0.75)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


# ------------------------------------------------------------------- 图：插入 1..7
def fig_insert7(path):
    q = BinQueue()
    states = []
    for k in range(1, 8):
        q.insert(k)
        assert q.size() == k, (k, q.size())
        states.append([(r, clone(t)) for r, t in q.forest()])

    fig, axes = plt.subplots(2, 4, figsize=(14.5, 7.2))
    axes = axes.ravel()
    for i, st in enumerate(states):
        ax = axes[i]
        draw_forest(ax, st, labels=["$B_{%d}$" % r for r, _ in st],
                    node_label=lambda n: str(n.key))
        ax.set_title("after insert %d   (%d = %s$_2$)"
                     % (i + 1, i + 1, bin(i + 1)[2:]), fontsize=10.5)
    ax = axes[7]
    ax.axis("off")
    ax.text(0.0, 1.0,
            "Insert 1, 2, ..., 7 into an initially\n"
            "empty binomial queue.\n\n"
            "The forest always matches the binary\n"
            "expansion of $N$, because there is at\n"
            "most one tree per height: bit $k$ of $N$\n"
            "is 1 iff $B_k$ is present.\n\n"
            "Insert 4 is the bad case -- two tree\n"
            "merges plus one stopping step.\n\n"
            "self-made figure: the structures are\n"
            "produced by the lecture's CombineTrees /\n"
            "Merge algorithm, not hand-drawn",
            fontsize=10, va="top", color="#333333")
    fig.suptitle(r"Binomial queue after each insertion: $B_k$ present iff the"
                 r" $k$-th bit of $N$ is 1", fontsize=12, y=0.99)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------- 图：DeleteMin 四步
def build_tree(rank, keys):
    """把已排序的 keys 摊进一棵 $B_{rank}$：根取最小，其余按孩子规模递减分配。"""
    assert len(keys) == 2 ** rank
    keys = sorted(keys)
    node = Node(keys[0])
    pos = 1
    for child_rank in range(rank - 1, -1, -1):
        take = 2 ** child_rank
        node.children.append(build_tree(child_rank, keys[pos:pos + take]))
        pos += take
    return node


def fig_deletemin(path):
    # H = {B3, B2, B0}，13 个元素（与图 1 的 size-13 例子同一形状；只画结构，不写键值）
    b3 = build_tree(3, [12, 13, 14, 16, 18, 21, 23, 24])
    b2 = build_tree(2, [24, 26, 51, 65])
    b0 = build_tree(0, [65])
    H = [(3, b3), (2, b2), (0, b0)]
    Hp = [(2, b2), (0, b0)]                                                  # H'：去掉 B3
    Hpp = [(2, b3.children[0]), (1, b3.children[1]), (0, b3.children[2])]    # H''：B3 的孩子
    # Step 4 由脚本真跑一遍 Merge(H', H'')（H' 与 H'' 都先深拷贝，免得改到上面画的面板）
    hq = BinQueue()
    hq.trees = {2: clone(b2), 0: clone(b0)}
    hq2 = BinQueue()
    hq2.trees = {2: clone(b3.children[0]), 1: clone(b3.children[1]), 0: clone(b3.children[2])}
    hq.merge(hq2)
    assert hq.size() == 12, hq.size()
    assert sorted(hq.trees) == [2, 3], sorted(hq.trees)          # 12 = 1100_2 = {B3, B2}
    result = hq.forest()

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.4))
    panels = [
        (H, r"$H$ = $\{B_3,B_2,B_0\}$ = 1101$_2$ (13 elements)",
         "the minimum sits at a root -- here the root of $B_3$"),
        (Hp, r"Step 2: cut $B_3$ out  $\Rightarrow$  $H'$ = $\{B_2,B_0\}$ (5 elements)", None),
        (Hpp, r"Step 3: strip the root of $B_3$  $\Rightarrow$  $H''$ (7 elements)",
         "its children, in decreasing rank: $B_2,B_1,B_0$"),
        (result, r"Step 4: Merge($H',H''$) = $\{B_3,B_2\}$ = 1100$_2$ (12 elements)",
         "$B_0{+}B_0\\to B_1$, then $B_1{+}B_1\\to B_2$, then $B_2{+}B_2\\to B_3$"),
    ]
    for ax, (forest, title, note) in zip(axes, panels):
        draw_forest(ax, forest, labels=["$B_{%d}$" % r for r, _ in forest])
        ax.set_title(title, fontsize=10.5)
        if note:
            ax.text(0.5, -0.02, note, transform=ax.transAxes, ha="center",
                    va="top", fontsize=9.5, color="#b03030")
    fig.suptitle("deleteMin in four steps: find the minimum, cut $B_k$ out ($H'$),"
                 " strip its root ($H''$), merge back -- self-made figure (structure only)",
                 fontsize=11.5, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fig_insert7(os.path.join(here, "fig_binomial_insert7.png"))
    fig_deletemin(os.path.join(here, "fig_binomial_deletemin.png"))
    print("done")

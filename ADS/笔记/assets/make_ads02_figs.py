#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADS02 讲义配图（自绘 / self-drawn）+ 讲义示例复算。

用于 `ADS/笔记/03_ADS02_红黑树与B+树.md`：

  1) fig_rb_insert_cases.png  红黑树插入 Case 1 / 2 / 3 的「处理前 / 处理后」对比（CLRS 13.3）
  2) fig_rb_delete_cases.png  红黑树删除 Case 1 / 2.1 / 2.2 / 3 → 4 的「处理前 / 处理后」对比（CLRS 13.4）
  3) fig_rb_insert_demo.png   讲义插入示例 11,14,2,7,8,15,5,4,1 的逐步复算
  4) fig_rb_delete_demo.png   讲义删除示例键集 10,5,15,3,7,6,8,11,17 的删除复算（覆盖全部 Case）
  5) fig_bplus_order4.png     讲义 B+ 树 [阶 4]（2-3-4 树）示例的结构
  6) fig_bplus_23_demo.png    讲义 B+ 树 [阶 3]（2-3 树）插入 18,1,19,28,70 的逐步复算

约定：
  * 图的标注统一用英文（与 `笔记/assets/` 下其他 ADS 配图一致），中文说明写在笔记正文里；
  * 红节点画成红色实心圆，黑节点画成深色实心圆；
  * 删除过程中「双黑」位置 x 用蓝色虚线圆标出（NIL 位置用虚线引到空的虚线圆上）。

运行：python3 make_ads02_figs.py   （图片写在脚本所在目录，dpi=160，白底）
"""
import bisect
import copy
import os
from math import ceil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

DPI = 160
OUT = os.path.dirname(os.path.abspath(__file__))

RED, BLACK = "R", "B"
C_RED, C_BLACK = "#d9534f", "#2b2b2b"
C_MARK, C_EDGE, C_BOX, C_BOX_E = "#1f6fb2", "#6b6b6b", "#eef4fb", "#3b6392"


# ==========================================================================
# 1. 红黑树（CLRS 13.3 / 13.4），并记录修复过程中触发的 Case 与当时的树形状
# ==========================================================================
class _Nil:
    color = BLACK
    key = None

    def __init__(self):
        self.p = self.left = self.right = self


NIL = _Nil()


class Node:
    def __init__(self, key, color=RED):
        self.key, self.color = key, color
        self.p = self.left = self.right = NIL


def serial(n):
    """把以 n 为根的子树序列化成嵌套 dict，便于画图。"""
    if n is NIL:
        return None
    return {"key": n.key, "color": n.color, "left": serial(n.left), "right": serial(n.right)}


class RBTree:
    """CLRS 红黑树；self.trace 记录每一步修复动作、执行后的树形状与「双黑」位置。"""

    def __init__(self):
        self.root = NIL
        self.trace = []

    # ---- 旋转（rotation） ----
    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not NIL:
            y.left.p = x
        y.p = x.p
        if x.p is NIL:
            self.root = y
        elif x is x.p.left:
            x.p.left = y
        else:
            x.p.right = y
        y.left = x
        x.p = y

    def right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right is not NIL:
            y.right.p = x
        y.p = x.p
        if x.p is NIL:
            self.root = y
        elif x is x.p.right:
            x.p.right = y
        else:
            x.p.left = y
        y.right = x
        x.p = y

    # ---- 插入（insertion） ----
    def insert(self, key):
        z = Node(key)
        y, x = NIL, self.root
        while x is not NIL:
            y = x
            x = x.left if key < x.key else x.right
        z.p = y
        if y is NIL:
            self.root = z
        elif key < y.key:
            y.left = z
        else:
            y.right = z
        self.fixup_insert(z)
        return z

    def _mark(self, x):
        """双黑位置：真实节点记 ('node', key)，NIL 记 ('nil', 父节点 key, 'L'/'R')。"""
        if x is NIL:
            if x.p is NIL:
                return ("root", None)
            return ("nil", x.p.key, "L" if x is x.p.left else "R")
        return ("node", x.key)

    def _snap(self, label, x):
        self.trace.append((label, serial(self.root), None if x is None else self._mark(x)))

    def fixup_insert(self, z):
        self._snap("PRE", z)
        while z.p.color == RED:
            gp = z.p.p
            sym = z.p is gp.right                      # sym 表示左右对称（镜像）的情形
            y = gp.left if sym else gp.right           # 叔节点（uncle）y
            if y.color == RED:                         # Case 1
                z.p.color = BLACK
                y.color = BLACK
                gp.color = RED
                self.trace.append(("CASE1", serial(self.root), self._mark(gp)))
                z = gp
            else:
                if (not sym and z is z.p.right) or (sym and z is z.p.left):   # Case 2
                    z = z.p
                    (self.right_rotate if sym else self.left_rotate)(z)
                    self.trace.append(("CASE2", serial(self.root), self._mark(z)))
                z.p.color = BLACK                                             # Case 3
                z.p.p.color = RED
                (self.left_rotate if sym else self.right_rotate)(z.p.p)
                self.trace.append(("CASE3", serial(self.root), self._mark(z)))
        self.root.color = BLACK

    # ---- 删除（deletion） ----
    def find(self, key):
        x = self.root
        while x is not NIL:
            if key == x.key:
                return x
            x = x.left if key < x.key else x.right
        return NIL

    def minimum(self, x):
        while x.left is not NIL:
            x = x.left
        return x

    def transplant(self, u, v):
        if u.p is NIL:
            self.root = v
        elif u is u.p.left:
            u.p.left = v
        else:
            u.p.right = v
        v.p = u.p

    def delete(self, key):
        z = self.find(key)
        if z is NIL:
            raise KeyError(key)
        y, y_color = z, z.color
        if z.left is NIL:
            x = z.right
            self.transplant(z, z.right)
        elif z.right is NIL:
            x = z.left
            self.transplant(z, z.left)
        else:
            y = self.minimum(z.right)
            y_color = y.color
            x = y.right
            if y.p is z:
                x.p = y
            else:
                self.transplant(y, y.right)
                y.right = z.right
                y.right.p = y
            self.transplant(z, y)
            y.left = z.left
            y.left.p = y
            y.color = z.color
        if y_color == BLACK:                 # 讲义：Adjust only if the node is black
            self.fixup_delete(x)
        return z

    def fixup_delete(self, x):
        self._snap("PRE", x)
        while x is not self.root and x.color == BLACK:
            sym = x is x.p.right
            w = x.p.left if sym else x.p.right
            if w.color == RED:                                       # Case 1
                w.color = BLACK
                x.p.color = RED
                (self.right_rotate if sym else self.left_rotate)(x.p)
                w = x.p.left if sym else x.p.right
                self.trace.append(("CASE1", serial(self.root), self._mark(x)))
            inner = w.right if sym else w.left                       # 靠 x 侧的侄子（nephew）
            outer = w.left if sym else w.right                       # 远离 x 的侄子
            if inner.color == BLACK and outer.color == BLACK:        # Case 2
                w.color = RED
                if x.p.color == RED:                                 # Case 2.1
                    x.p.color = BLACK
                    self.trace.append(("CASE2.1", serial(self.root), self._mark(x)))
                    x = self.root
                    break
                self.trace.append(("CASE2.2", serial(self.root), self._mark(x.p)))
                x = x.p                                              # Case 2.2：双黑上移
                continue
            if outer.color == BLACK:                                 # Case 3
                inner.color = BLACK
                w.color = RED
                (self.left_rotate if sym else self.right_rotate)(w)
                w = x.p.left if sym else x.p.right
                self.trace.append(("CASE3", serial(self.root), self._mark(x)))
            w.color = x.p.color                                      # Case 4
            x.p.color = BLACK
            (w.left if sym else w.right).color = BLACK
            (self.right_rotate if sym else self.left_rotate)(x.p)
            self.trace.append(("CASE4", serial(self.root), self._mark(x)))
            x = self.root
        x.color = BLACK

    # ---- 自检与构造 ----
    def check(self):
        keys = []

        def inorder(n):
            if n is NIL:
                return
            inorder(n.left)
            keys.append(n.key)
            inorder(n.right)

        inorder(self.root)
        assert keys == sorted(keys), "BST 顺序被破坏"
        assert self.root.color == BLACK, "根必须是黑色"
        assert len(set(keys)) == len(keys), "出现重复键"

        def black_count(n):
            if n is NIL:
                return 1                       # NIL 记为黑
            if n.color == RED:
                assert n.left.color == BLACK and n.right.color == BLACK, "出现红-红"
            return black_count(n.left) + (0 if n.color == RED else 1)

        def walk(n):
            if n is NIL:
                return 0
            assert black_count(n.left) == black_count(n.right), "黑高（black height）不相等"
            return 1 + max(walk(n.left), walk(n.right))

        return walk(self.root)

    def build(self, keys):
        for k in keys:
            self.insert(k)
        self.trace.clear()
        return self

    def make_tree(self, spec):
        """按 (key, color, left, right) 嵌套 spec 显式构造一棵红黑树（用于设计 Case 示例）。"""

        def rec(s, parent):
            if s is None:
                return NIL
            k, c, l, r = s
            n = Node(k, c)
            n.p = parent
            n.left = rec(l, n)
            n.right = rec(r, n)
            return n

        self.root = rec(spec, NIL)
        self.trace.clear()
        self.check()                     # 构造出来的树必须满足红黑性质
        return self


# ==========================================================================
# 2. 画树
# ==========================================================================
def _layout(ser, depth, counter, pos):
    if ser is None:
        return
    _layout(ser["left"], depth + 1, counter, pos)
    pos[id(ser)] = (counter[0], -depth)
    counter[0] += 1
    _layout(ser["right"], depth + 1, counter, pos)


def draw_tree(ax, ser, title="", mark=None, labels=None, rad=0.30, fs=10, hi=None, ghost=None):
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=fs, pad=5)
    if ser is None:
        return
    pos, counter = {}, [0]
    _layout(ser, 0, counter, pos)

    def walk(s, fn):
        if s is None:
            return
        fn(s)
        walk(s["left"], fn)
        walk(s["right"], fn)

    def edge(s):
        for ch in ("left", "right"):
            c = s[ch]
            if c is not None:
                ax.plot(*zip(pos[id(s)], pos[id(c)]), color=C_EDGE, lw=1.1, zorder=1)
                edge(c)

    def node(s):
        x, y = pos[id(s)]
        ax.add_patch(Circle((x, y), rad, facecolor=C_RED if s["color"] == RED else C_BLACK,
                            edgecolor="#1a1a1a", lw=1.0, zorder=3))
        ax.text(x, y, str(s["key"]), ha="center", va="center", color="white", fontsize=fs - 1, zorder=4)
        if labels and s["key"] in labels:
            ax.text(x - rad * 1.15, y + rad * 0.9, labels[s["key"]], ha="center", va="bottom",
                    fontsize=fs - 1, style="italic", color=C_MARK, zorder=5)

    walk(ser, edge)
    walk(ser, node)

    if mark is not None:
        if mark[0] == "node":
            def m(s):
                if s["key"] == mark[1]:
                    x, y = pos[id(s)]
                    ax.add_patch(Circle((x, y), rad * 1.45, facecolor="none", edgecolor=C_MARK,
                                        lw=1.6, ls=(0, (2.5, 2)), zorder=5))
                    ax.text(x - rad * 2.2, y - rad * 1.2, "x", fontsize=fs, color=C_MARK, zorder=6)
            walk(ser, m)
        else:
            _, pkey, side = mark

            def m2(s):
                if s["key"] == pkey:
                    x, y = pos[id(s)]
                    mx, my = x + (-0.62 if side == "L" else 0.62), y - 1
                    ax.plot([x, mx], [y - rad, my], color=C_EDGE, lw=0.9, ls=":", zorder=1)
                    ax.add_patch(Circle((mx, my), rad * 0.95, facecolor="none", edgecolor=C_MARK,
                                        lw=1.6, ls=(0, (2.5, 2)), zorder=5))
                    ax.text(mx, my, "x", ha="center", va="center", fontsize=fs - 1, color=C_MARK, zorder=6)
                    ax.text(mx, my - rad - 0.2, "+1 black", ha="center", va="top", fontsize=fs - 3,
                            color=C_MARK, zorder=6)
            walk(ser, m2)

    if hi is not None:                      # 高亮「即将被删除」的节点
        def h(s):
            if s["key"] == hi:
                x, y = pos[id(s)]
                ax.add_patch(Circle((x, y), rad * 1.45, facecolor="none", edgecolor="#c0392b",
                                    lw=1.8, ls=(0, (4, 2)), zorder=6))
                ax.text(x, y - rad * 2.1, "delete %s" % hi, ha="center", va="top",
                        fontsize=fs - 1, color="#c0392b", zorder=6)
        walk(ser, h)

    if ghost is not None:                   # 标出被删节点原来所在的位置
        pkey, side, gtext = ghost

        def g(s):
            if s["key"] == pkey:
                x, y = pos[id(s)]
                mx, my = x + (-0.62 if side == "L" else 0.62), y - 1
                ax.plot([x, mx], [y - rad, my], color=C_EDGE, lw=0.9, ls=":", zorder=1)
                ax.add_patch(Circle((mx, my), rad * 0.95, facecolor="none", edgecolor="#9a9a9a",
                                    lw=1.4, ls=(0, (2.5, 2)), zorder=5))
                ax.text(mx, my, gtext, ha="center", va="center", fontsize=fs - 2, color="#8a8a8a", zorder=6)
                ax.text(mx, my - rad - 0.2, "deleted", ha="center", va="top", fontsize=fs - 4,
                        color="#8a8a8a", zorder=6)
        walk(ser, g)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1.2, max(xs) + 1.2)
    ax.set_ylim(min(ys) - 1.8, max(ys) + 1.2)
    ax.set_aspect("equal")


def note_box(ax, lines, fs=10):
    ax.set_axis_off()
    ax.text(0.0, 1.0, "\n".join(lines), fontsize=fs, va="top", ha="left", linespacing=1.6)


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


# ==========================================================================
# 3. 插入的三种情形
# ==========================================================================
def fig_insert_cases():
    # Case 1：在 {10,5,15} 中插入 1 —— 父 5 红、叔 15 红
    t = RBTree().build([10, 5, 15])
    t.trace.clear()
    t.insert(1)
    c1 = t.trace
    assert [e[0] for e in c1] == ["PRE", "CASE1"], [e[0] for e in c1]

    # Case 2 → Case 3：在 {10,5} 中插入 8 —— 8 是「内侧」孩子
    t2 = RBTree().build([10, 5])
    t2.trace.clear()
    t2.insert(8)
    c2 = t2.trace
    assert [e[0] for e in c2] == ["PRE", "CASE2", "CASE3"], [e[0] for e in c2]

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.2))
    draw_tree(axes[0][0], c1[0][1], "Case 1: uncle is red  (before)", mark=None,
              labels={1: "z", 5: "p", 15: "y", 10: "g"})
    draw_tree(axes[0][1], c1[1][1], "Case 1: recolor p and y, g turns red  (after)")
    note_box(axes[0][2], [
        "Insertion, Case 1: uncle y is red",
        "1. color p and y black, g red",
        "2. z <- g  (violation moves up 2 levels)",
        "3. if g is the root, paint it black at the end",
        "-> recursion / reduction, no rotation here",
    ])
    draw_tree(axes[1][0], c2[0][1], "Case 2: z is an inner child  (before)", mark=None,
              labels={8: "z", 5: "p", 10: "g"})
    draw_tree(axes[1][1], c2[1][1], "Case 2: one rotation, becomes Case 3",
              labels={5: "z", 8: "p", 10: "g"})
    draw_tree(axes[1][2], c2[2][1], "Case 3: recolor + one rotation  (done)",
              labels={10: "g"})
    fig.suptitle("Red-black tree insertion: Case 1 / 2 / 3   (self-drawn, generated by make_ads02_figs.py)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "fig_rb_insert_cases.png")
    print("  insert Case1 trace:", [e[0] for e in c1])
    print("  insert Case2/3 trace:", [e[0] for e in c2])


# ==========================================================================
# 4. 删除的四种情形
# ==========================================================================
def fig_delete_cases():
    """四个 Case 各给一个具体例子：先画出「原树 + 红虚线标出要删的键」，再画出删除后待修复的状态，
    最后画修复过程中的每一步（自绘；示例树先用 check() 校验红黑性质，再跑真实删除）。"""
    leaf = lambda k, c=None: (k, c or BLACK, None, None)
    cases = []

    def run(spec, key, names):
        t = RBTree().make_tree(spec)
        before = serial(t.root)
        t.trace.clear()
        t.delete(key)
        return {"key": key, "before": before, "trace": t.trace, "names": names}

    # Case 1：兄弟 w 红
    cases.append(run((20, BLACK,
                      (10, BLACK, leaf(5), (12, RED, leaf(11), leaf(13))),
                      (30, BLACK, leaf(25), leaf(35))), 5,
                     {"before": {10: "p", 12: "w"}, "mid": {}, "final": {}}))
    # Case 2.1：w 黑、两侄皆黑、父节点红
    cases.append(run((20, BLACK,
                      (10, RED, leaf(5), leaf(12)),
                      leaf(30)), 5,
                     {"before": {10: "p", 12: "w"}, "mid": {}, "final": {}}))
    # Case 2.2：w 黑、两侄皆黑、父节点黑
    cases.append(run((20, BLACK,
                      (10, BLACK, leaf(5), leaf(12)),
                      (30, BLACK, leaf(25), leaf(35))), 5,
                     {"before": {10: "p", 12: "w"}, "mid": {}, "final": {}}))
    # Case 3 → Case 4：内侄红、外侄黑
    cases.append(run((20, BLACK,
                      (10, RED, leaf(5), (12, BLACK, (11, RED, None, None), None)),
                      leaf(30)), 5,
                     {"before": {10: "p", 12: "w", 11: "inner"}, "mid": {11: "w"}, "final": {}}))

    for c in cases:
        assert len(c["trace"]) >= 2, c["trace"]
        print("  delete %d: %s" % (c["key"], [e[0] for e in c["trace"]]))

    notes = [
        ["This row ends at column 3:", "Case 2.1 already finished", "the fix-up (no rotation,", "only a recolor)."],
        ["Keep pushing '+1 black' up", "until either", "x becomes the root, or", "Case 2.1 / 4 ends it."],
    ]
    fig, axes = plt.subplots(4, 4, figsize=(17.5, 15.6))
    for i, c in enumerate(cases):
        k, tr, nm = c["key"], c["trace"], c["names"]
        draw_tree(axes[i][0], c["before"], "1) the tree, node %d dashed red = to be deleted" % k, hi=k)
        draw_tree(axes[i][1], tr[0][1],
                  "2) after deleting %d, before fix-up: x carries '+1 black'" % k,
                  mark=tr[0][2], labels=nm["before"])
        draw_tree(axes[i][2], tr[1][1],
                  "3) after %s" % tr[1][0].replace("CASE", "Case "),
                  mark=(tr[1][2] if tr[1][0].startswith("CASE2.2") else None), labels=nm["mid"])
        if len(tr) >= 3:
            draw_tree(axes[i][3], tr[2][1], "4) after %s  (done)" % tr[2][0].replace("CASE", "Case "),
                      labels=nm["final"])
        else:
            note_box(axes[i][3], notes[0] if tr[1][0] == "CASE2.1" else notes[1], fs=10)
    fig.suptitle("Red-black tree deletion: a concrete example for every case "
                 "(each row: the tree -> delete the dashed node -> fix-up)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    save(fig, "fig_rb_delete_cases.png")


# ==========================================================================
# 5. 讲义示例复算：红黑树插入 / 删除
# ==========================================================================
def fig_insert_demo():
    """讲义插入示例序列 11,14,2,7,8,15,5,4,1 的逐步复算（每步标出触发的 Case）。"""
    seq = [11, 14, 2, 7, 8, 15, 5, 4, 1]
    t = RBTree()
    steps = []
    for k in seq:
        t.trace.clear()
        t.insert(k)
        steps.append((k, [e[0] for e in t.trace], serial(t.root)))
    t.check()

    fig, axes = plt.subplots(3, 3, figsize=(13.5, 10.4))
    for i, (k, cases, ser) in enumerate(steps):
        ax = axes[i // 3][i % 3]
        cases = [c for c in cases if c != "PRE"]
        title = "after insert %d" % k
        if cases:
            title += "   -> " + " + ".join(c.replace("CASE", "Case ") for c in cases)
        draw_tree(ax, ser, title, fs=10)
    fig.suptitle("Lecture example: inserting 11,14,2,7,8,15,5,4,1   "
                 "(self-drawn; recomputed by the script)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save(fig, "fig_rb_insert_demo.png")
    print("  insert demo:", [(k, c) for k, c, _ in steps])
    return steps


def fig_delete_demo():
    """讲义键集 10,5,15,3,7,6,8,11,17：把需要修复的四次删除做成「删除前 / 删除后」对照图。"""
    keys = [10, 5, 15, 3, 7, 6, 8, 11, 17]
    deletes = [3, 17, 15, 8, 11, 7, 5]
    t = RBTree().build(keys)
    t.check()
    steps = []
    for d in deletes:
        z = t.find(d)
        pkey = None if z.p is NIL else z.p.key
        side = None if z.p is NIL else ("L" if z is z.p.left else "R")
        deg = (0 if z.left is NIL else 1) + (0 if z.right is NIL else 1)
        before = serial(t.root)
        t.trace.clear()
        t.delete(d)
        steps.append({"key": d, "before": before, "after": serial(t.root),
                      "cases": [e[0] for e in t.trace if e[0] != "PRE"],
                      "ghost": None if (deg == 2 or pkey is None) else (pkey, side, str(d))})
    t.check()
    print("  delete demo:", [(s["key"], s["cases"]) for s in steps])

    shown = [s for s in steps if s["cases"]]
    skipped = [str(s["key"]) for s in steps if not s["cases"]]
    assert len(shown) == 4, shown
    fig, axes = plt.subplots(2, 4, figsize=(18.0, 9.6))
    for i, st in enumerate(shown):
        ax0, ax1 = axes[i // 2][(i % 2) * 2], axes[i // 2][(i % 2) * 2 + 1]
        draw_tree(ax0, st["before"], "before deleting %d  (dashed red = the node to delete)" % st["key"],
                  hi=st["key"])
        ttl = "after deleting %d" % st["key"]
        if st["cases"]:
            ttl += "   -> " + " + ".join(c.replace("CASE", "Case ") for c in st["cases"])
        draw_tree(ax1, st["after"], ttl, ghost=st["ghost"])
    fig.suptitle("Lecture key set 10,5,15,3,7,6,8,11,17: the four deletions that need a fix-up "
                 "(the other deletions %s need no fix-up)" % ", ".join(skipped), fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "fig_rb_delete_demo.png")
    return steps


# ==========================================================================
# 6. B+ 树（B+ tree）：讲义阶 4 示例 + 阶 3 插入复算
# ==========================================================================
class BNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []          # 非叶节点用
        self.next = None            # 叶子之间的链表指针（讲义图上的 >>>）
        self.parent = None


class BPlusTree:
    """B+ 树 [阶 M]：叶子存放全部数据，内部节点只放索引（M-1 个键）。

    分裂规则按讲义代码：节点有 M+1 个键时，分裂成 ⌈(M+1)/2⌉ 与 ⌊(M+1)/2⌋ 个键的两半。
    """

    def __init__(self, M):
        self.M = M
        self.root = BNode(True)

    # ---- 查找 ----
    def find(self, x):
        n = self.root
        while not n.leaf:
            idx = bisect.bisect_right(n.keys, x)
            n = n.children[idx]
        return x in n.keys

    def _leaf_of(self, x):
        n = self.root
        while not n.leaf:
            n = n.children[bisect.bisect_right(n.keys, x)]
        return n

    # ---- 插入 ----
    def insert(self, x):
        leaf = self._leaf_of(x)
        bisect.insort(leaf.keys, x)
        if len(leaf.keys) > self.M:
            self._split_leaf(leaf)

    def _split_leaf(self, leaf):
        k = (self.M + 2) // 2               # ⌈(M+1)/2⌉
        new = BNode(True)
        new.keys = leaf.keys[k:]
        leaf.keys = leaf.keys[:k]
        new.next = leaf.next
        leaf.next = new
        self._insert_child(leaf, new.keys[0], new)

    def _insert_child(self, left, key, right):
        """把 (key, right) 插到 left 的父节点中；必要时递归分裂。"""
        p = left.parent
        if p is None:
            root = BNode(False)
            root.keys = [key]
            root.children = [left, right]
            left.parent = right.parent = root
            self.root = root
            return
        i = p.children.index(left)
        p.keys.insert(i, key)
        p.children.insert(i + 1, right)
        right.parent = p
        if len(p.children) > self.M:
            self._split_interior(p)

    def _split_interior(self, node):
        m = (len(node.children) + 1) // 2
        up = node.keys[m - 1]
        new = BNode(False)
        new.keys = node.keys[m:]
        new.children = node.children[m:]
        node.keys = node.keys[:m - 1]
        node.children = node.children[:m]
        for c in new.children:
            c.parent = new
        self._insert_child(node, up, new)

    # ---- 自检 ----
    def check(self):
        keys, depth = [], {}

        def walk(n, d):
            if n.leaf:
                assert len(n.keys) <= self.M, "叶子键太多"
                if n is not self.root:
                    assert len(n.keys) >= ceil(self.M / 2), "叶子键太少"
            else:
                assert len(n.keys) <= self.M - 1, "内部节点键太多"
                if n is self.root:
                    assert 2 <= len(n.children) <= self.M, "根孩子数不合法"
                else:
                    assert ceil((self.M + 1) / 2) <= len(n.children) <= self.M, "非根内部节点孩子数不合法"
            depth[id(n)] = d
            if n.leaf:
                keys.extend(n.keys)
                return [d]
            out = []
            for c in n.children:
                out += walk(c, d + 1)
            return out

        if self.root.leaf:
            keys = list(self.root.keys)
        else:
            ds = walk(self.root, 0)
            assert len(set(ds)) == 1, "叶子深度不同"
        assert keys == sorted(keys), "叶子键未排序"
        return depth

    def levels(self):
        out, cur = [], [self.root]
        while cur:
            out.append(cur)
            cur = [c for n in cur if not n.leaf for c in n.children]
        return out

    def leaf_chain(self):
        n = self.root
        while not n.leaf:
            n = n.children[0]
        out = []
        while n is not None:
            out.append(n)
            n = n.next
        return out


def _min_key(n):
    while not n.leaf:
        n = n.children[0]
    return n.keys[0]


def bplus_build(M, leafsets, groups):
    """按讲义图构造一棵 B+ 树：leafsets 给出各叶子的键，groups 给出叶子在第 2 层的分组。

    内部节点的键 = 「除第 1 个子树外，各子树中的最小键」（讲义原话）。
    """
    tree = BPlusTree(M)
    leaves = []
    for ks in leafsets:
        lf = BNode(True)
        lf.keys = list(ks)
        leaves.append(lf)
    for i in range(len(leaves) - 1):
        leaves[i].next = leaves[i + 1]
    nodes = []
    for a, b in groups:
        n = BNode(False)
        n.children = leaves[a:b]
        for c in n.children:
            c.parent = n
        n.keys = [_min_key(c) for c in n.children[1:]]
        nodes.append(n)
    if len(nodes) == 1:
        tree.root = nodes[0]
    else:
        root = BNode(False)
        root.children = nodes
        for c in nodes:
            c.parent = root
        root.keys = [_min_key(c) for c in nodes[1:]]
        tree.root = root
    tree.check()
    return tree


def draw_bplus(ax, tree, title="", fs=9):
    """画一棵 B+ 树：叶子在最下一行（带 >>> 链表箭头），内部节点在上。"""
    ax.set_axis_off()
    ax.set_title(title, fontsize=fs + 1, pad=5)
    levels = tree.levels()
    leaves = tree.leaf_chain()
    w, gap = 1.0, 0.35
    leaf_x, x = [], 0.0
    for lf in leaves:
        leaf_x.append(x)
        x += len(lf.keys) + gap
    top = len(levels) - 1
    pos = {}
    for i, lf in enumerate(leaves):
        pos[id(lf)] = (leaf_x[i], 0.0)
    for d in range(top - 1, -1, -1):
        for n in levels[d]:
            xs = [pos[id(c)][0] for c in n.children]
            pos[id(n)] = (0.5 * (min(xs) + max(xs)), float(top - d))

    def box(px, py, keys, width, color=C_BOX):
        ax.add_patch(Rectangle((px, py - 0.22), width, 0.44, facecolor=color,
                               edgecolor=C_BOX_E, lw=1.1, zorder=3))
        for i, k in enumerate(keys):
            ax.text(px + 0.5 + i, py, str(k), ha="center", va="center", fontsize=fs, zorder=4)

    for n in [x for lv in levels for x in lv]:
        px, py = pos[id(n)]
        width = max(len(n.keys), 1)
        box(px - width / 2.0, py, n.keys, width)
    for n in [x for lv in levels for x in lv]:
        if n.leaf:
            continue
        px, py = pos[id(n)]
        width = max(len(n.keys), 1)
        for i, c in enumerate(n.children):
            cx, cy = pos[id(c)]
            # 第 i 个孩子挂在第 i 条分隔线下方：0/1/2 -> 左端/键 i-1 处/右端
            off = (-width / 2.0 + 0.5) if i == 0 else (width / 2.0 - 0.5) if i == len(n.children) - 1 \
                else (-width / 2.0 + i + 0.5)
            ax.plot([px + off, cx], [py - 0.22, cy + 0.22], color=C_EDGE, lw=1.1, zorder=1)
    for i in range(len(leaves) - 1):
        n, m = leaves[i], leaves[i + 1]
        x1 = pos[id(n)][0] + max(len(n.keys), 1) / 2.0
        x2 = pos[id(m)][0] - max(len(m.keys), 1) / 2.0
        ax.add_patch(FancyArrowPatch((x1, 0.0), (x2, 0.0), arrowstyle="-|>", mutation_scale=9,
                                     color="#8a8a8a", lw=1.0, zorder=2))
    xs = [p[0] for p in pos.values()]
    ax.set_xlim(min(xs) - 1.4, max(xs) + 1.4)
    ax.set_ylim(-0.9, top + 0.7)
    ax.set_aspect("equal")


def fig_bplus_order4():
    """讲义 B+ 树 [阶 4]（2-3-4 树）示例：结构按讲义图，键值取自讲义文字。"""
    M = 4
    leafsets = [[1, 4, 8, 11], [12, 13], [15, 18, 19], [21, 24], [25, 26], [31, 38],
                [41, 43, 46], [48, 49, 50], [59, 68], [72, 78], [84, 88], [91, 92, 99]]
    tree = bplus_build(M, leafsets, [(0, 4), (4, 8), (8, 12)])
    assert tree.root.keys == [25, 59], tree.root.keys
    assert [n.keys for n in tree.root.children] == [[12, 15, 21], [31, 41, 48], [72, 84, 91]]

    fig, ax = plt.subplots(figsize=(14.0, 4.6))
    draw_bplus(ax, tree, "A B+ tree of order 4 (2-3-4 tree), from the lecture: all records live in the leaves, "
                         "linked by >>>", fs=9)
    save(fig, "fig_bplus_order4.png")
    print("  B+ order 4: interior keys", [n.keys for n in tree.root.children], "root", tree.root.keys)


def fig_bplus_23_demo():
    """讲义 B+ 树 [阶 3]（2-3 树）示例：Find 52，再依次 Insert 18, 1, 19, 28, 70。"""
    tree = bplus_build(3, [[8, 11, 12], [16, 17], [22, 23, 31], [41, 52], [58, 59, 61]],
                       [(0, 2), (2, 5)])
    states = [("initial tree   (Find 52: root -> 41:58 -> leaf 41,52)", copy.deepcopy(tree))]
    for x in [18, 1, 19, 28, 70]:
        tree.insert(x)
        tree.check()
        states.append(("after Insert %d" % x, copy.deepcopy(tree)))
        print("  B+ order 3 after Insert %-3d leaves: %s | 2nd-level keys: %s | root: %s"
              % (x, [l.keys for l in tree.leaf_chain()],
                 [n.keys for n in (tree.root.children if not tree.root.leaf else [])], tree.root.keys))

    fig, axes = plt.subplots(2, 3, figsize=(14.0, 8.0))
    for i, (title, tr) in enumerate(states):
        draw_bplus(axes[i // 3][i % 3], tr, title, fs=9)
    fig.suptitle("A B+ tree of order 3 (2-3 tree), from the lecture: Find 52, then Insert 18, 1, 19, 28, 70   "
                 "(self-drawn; recomputed by the script)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "fig_bplus_23_demo.png")


if __name__ == "__main__":
    fig_insert_cases()
    fig_delete_cases()
    fig_insert_demo()
    fig_delete_demo()
    fig_bplus_order4()
    fig_bplus_23_demo()

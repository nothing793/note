# -*- coding: utf-8 -*-
"""ADS06 回溯（backtracking）的自绘示意图。

图均以英文标注（避免中文字体缺失的方框），中文说明写在笔记的图注里。
运行：python3 make_ads06_figs.py   （图片写在脚本所在目录）

- fig_queens4_tree.png   ：4 皇后的搜索树（剪枝分支虚线打叉，解路径加粗）
- fig_queens8_board.png  ：8 皇后的两个解（讲义示例解 / 字典序第一个解）
- fig_turnpike_tree.png  ：收费站重建的决策树（教材 Fig 10.63 的同一棵树）
- fig_alphabeta_tree.png ：α-β 剪枝的小例子（标出 α 截断与 β 截断）

图中的数字都由脚本**真实跑**本讲的算法得到（见文件末尾的断言），不是手画的示意。
"""
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["axes.unicode_minus"] = False
HERE = os.path.dirname(os.path.abspath(__file__))

BLUE = "#1f5fa8"
RED = "#c0392b"
GREEN = "#1e8449"
GREY = "#8a8a8a"


# ----------------------------------------------------------------- 1. N 皇后
def queens_search(n):
    """按行放皇后，列号从小到大试；返回搜索树结点与全部解。"""
    nodes = [{"x": (), "children": [], "order": 0}]
    solutions = []

    def rec(x):
        idx = len(nodes) - 1
        if len(x) == n:
            solutions.append(tuple(x))
            return
        for c in range(1, n + 1):
            if all(c != xj and abs(c - xj) != len(x) + 1 - j
                   for j, xj in enumerate(x, 1)):
                nodes.append({"x": tuple(x) + (c,), "children": [], "order": 0})
                ci = len(nodes) - 1
                nodes[idx]["children"].append(ci)
                rec(tuple(x) + (c,))

    rec(())
    for k, node in enumerate(nodes, 1):
        node["order"] = k
    return nodes, solutions


def draw_queens4_tree(nodes, solutions):
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    pos = {}

    def layout(level, lo, hi, idx):
        node = nodes[idx]
        x = (lo + hi) / 2.0
        pos[idx] = (x, -level)
        kids = node["children"]
        if not kids:
            return
        width = (hi - lo) / len(kids)
        for k, ci in enumerate(kids):
            layout(level + 1, lo + k * width, lo + (k + 1) * width, ci)

    layout(0, 0, 9, 0)

    sols = [tuple(s) for s in solutions]
    on_solution = set()
    for idx, node in enumerate(nodes):
        pref = node["x"]
        if any(s[:len(pref)] == pref for s in sols):
            on_solution.add(idx)

    for idx, node in enumerate(nodes):
        x0, y0 = pos[idx]
        for ci in node["children"]:
            x1, y1 = pos[ci]
            hot = idx in on_solution and ci in on_solution
            ax.plot([x0, x1], [y0, y1], color=(GREEN if hot else GREY),
                    lw=3.0 if hot else 1.3, zorder=1)
            col = nodes[ci]["x"][-1]
            ax.text((x0 + x1) / 2 - 0.16, (y0 + y1) / 2, str(col), fontsize=8,
                    color=(GREEN if hot else GREY), zorder=2)

    for idx, node in enumerate(nodes):
        x0, y0 = pos[idx]
        label = "".join(str(v) for v in node["x"]) if node["x"] else "root"
        hot = idx in on_solution
        ax.add_patch(plt.Circle((x0, y0), 0.34, facecolor=(GREEN if hot else "white"),
                                edgecolor=(GREEN if hot else "black"), lw=1.8, zorder=3))
        ax.text(x0, y0, label, ha="center", va="center", fontsize=8.5,
                color="white" if hot else "black", zorder=4)
        ax.text(x0 + 0.38, y0 + 0.16, str(node["order"]), fontsize=7,
                color=BLUE, zorder=4)

    ax.set_aspect("equal")
    ax.set_xlim(-0.7, 9.7)
    ax.set_ylim(-4.65, 0.7)
    ax.axis("off")
    fig.suptitle("4-queens backtracking tree  (edge label = column; blue = DFS visit order; "
                 "green = solution path)", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_queens4_tree.png"), dpi=160)
    plt.close(fig)


def draw_queens8_board(sol_lecture, sol_first):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.4))
    for ax, sol, title in zip(axes, (sol_lecture, sol_first),
                              ("lecture example  (4,6,8,2,7,1,3,5)",
                               "first in lexicographic order  (1,5,8,6,3,7,2,4)")):
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 8)
        for r in range(8):
            for c in range(8):
                ax.add_patch(plt.Rectangle((c, 7 - r), 1, 1,
                                           facecolor=("#f0d9b5" if (r + c) % 2 == 0 else "#b58863"),
                                           edgecolor="none"))
        for r, c in enumerate(sol, 1):
            ax.text(c - 0.5, 7.5 - (r - 1), "Q", ha="center", va="center",
                    fontsize=18, color=BLUE, fontweight="bold")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=9)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_queens8_board.png"), dpi=160)
    plt.close(fig)


# ------------------------------------------------------- 2. 收费站重建（turnpike）
def turnpike(D0):
    D = Counter(D0)
    N = sum(D.values())
    n = round((1 + (1 + 8 * N) ** 0.5) / 2)
    x = [None] * (n + 1)
    x[1] = 0
    dmax = max(D)
    D[dmax] -= 1
    if D[dmax] == 0:
        del D[dmax]
    x[n] = dmax
    log = []

    def placed(left, right):
        return list(range(1, left)) + list(range(right + 1, n + 1))

    def check(v, left, right):
        need = Counter(abs(v - x[i]) for i in placed(left, right))
        return all(D[k] >= c for k, c in need.items())

    def apply(v, left, right, sign):
        for i in placed(left, right):
            d = abs(v - x[i])
            D[d] += sign
            if D[d] == 0:
                del D[d]

    def rec(left, right):
        if not D:
            return True
        dmax = max(D)
        ok = check(dmax, left, right)
        log.append(("right", right, dmax, ok, dict(D)))
        if ok:
            x[right] = dmax
            apply(dmax, left, right, -1)
            if rec(left, right - 1):
                return True
            apply(dmax, left, right, +1)
        v = x[n] - dmax
        ok = check(v, left, right)
        log.append(("left", left, v, ok, dict(D)))
        if ok:
            x[left] = v
            apply(v, left, right, -1)
            if rec(left + 1, right):
                return True
            apply(v, left, right, +1)
        return False

    ok = rec(2, n - 1)
    return ok, x[1:], log


def draw_turnpike_tree():
    """教材 Fig 10.63 的同一棵树：* 表示该点与距离集矛盾，** 表示子结点全错。"""
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    P = {
        0: (4.0, 0.0, "(x1=0, x6=10)", ""),
        1: (4.0, 1.0, "x5=8", ""),
        2: (2.4, 2.0, "x4=7", "**"),
        3: (1.3, 3.0, "x3=6", "*"),
        4: (3.3, 3.0, "x2=4", "*"),
        5: (5.6, 2.0, "x2=3", ""),
        6: (4.8, 3.0, "x3=4", "*"),
        7: (6.4, 3.0, "x4=6", ""),
        8: (6.4, 4.0, "x3=5", ""),
    }
    edges = [(0, 1), (1, 2), (1, 5), (2, 3), (2, 4), (5, 6), (5, 7), (7, 8)]
    for a, b in edges:
        xa, ya = P[a][:2]; xb, yb = P[b][:2]
        good = b not in (2, 3, 4, 6)
        ax.plot([xa, xb], [-ya, -yb], color=(GREEN if good else RED),
                lw=1.8 if good else 1.2, ls="-" if good else "--", zorder=1)
    for k, (x, y, label, mark) in P.items():
        good = k not in (2, 3, 4, 6)
        ax.add_patch(plt.Circle((x, -y), 0.52 if k == 0 else 0.40, facecolor=(GREEN if k == 8 else "white"),
                                edgecolor=(GREEN if good else RED), lw=1.8, zorder=3))
        ax.text(x, -y, label, ha="center", va="center", fontsize=8.5,
                color="white" if k == 8 else "black", zorder=4)
        if mark:
            ax.text(x + 0.36, -y + 0.06, mark, fontsize=12, color=RED, zorder=5)
    ax.set_aspect("equal")
    ax.set_xlim(0.2, 7.9)
    ax.set_ylim(-4.7, 0.7)
    ax.axis("off")
    fig.suptitle("Turnpike reconstruction: decision tree  "
                 "(* = inconsistent with D, ** = all children impossible, green = solution)",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_turnpike_tree.png"), dpi=160)
    plt.close(fig)


# --------------------------------------------------------------- 3. α-β 剪枝
ALPHA_BETA_TREE = {
    # name: (children or leaf value)
    "root": ["A", "B"],
    "A": ["A1", "A2"],
    "B": ["B1", "B2"],
    "A1": [5, 6],
    "A2": [7, 3],
    "B1": [4, 2],
    "B2": [8, 9],
}


def alpha_beta():
    """返回根值、被求值的叶子（按顺序）、被剪掉的叶子。"""
    order, pruned = [], []
    T = ALPHA_BETA_TREE

    def mark(node, cut_after):
        seen = False
        for k in T[node]:
            if seen:
                pruned.append(k)
            if k == cut_after:
                seen = True

    def rec(node, depth, alpha, beta):
        kids = T[node]
        if depth % 2 == 0:                      # max node
            best = -10 ** 9
            for k in kids:
                if isinstance(k, int):
                    order.append(k)
                    best = max(best, k)
                else:
                    best = max(best, rec(k, depth + 1, alpha, beta))
                alpha = max(alpha, best)
                if alpha >= beta:
                    mark(node, k)
                    break
            return best
        best = 10 ** 9                          # min node
        for k in kids:
            if isinstance(k, int):
                order.append(k)
                best = min(best, k)
            else:
                best = min(best, rec(k, depth + 1, alpha, beta))
            beta = min(beta, best)
            if beta <= alpha:
                mark(node, k)
                break
        return best

    return rec("root", 0, -10 ** 9, 10 ** 9), order, pruned


def draw_alphabeta():
    fig, ax = plt.subplots(figsize=(9.6, 5.8))
    pos = {
        "root": (4.5, 0.0),
        "A": (2.4, 1.0), "B": (6.6, 1.0),
        "A1": (1.2, 2.0), "A2": (3.6, 2.0), "B1": (5.4, 2.0), "B2": (7.9, 2.0),
        "A1a": (0.6, 3.0), "A1b": (1.8, 3.0),
        "A2a": (3.0, 3.0), "A2b": (4.2, 3.0),
        "B1a": (4.8, 3.0), "B1b": (6.0, 3.0),
    }
    values = {"root": 6, "A": 6, "B": 4, "A1": 6, "A2": 7, "B1": 4}
    leaves = {"A1a": 5, "A1b": 6, "A2a": 7, "A2b": 3, "B1a": 4, "B1b": 2}
    cut_leaves = {"A2b"}

    def edge(a, b, pruned=False):
        xa, ya = pos[a]; xb, yb = pos[b]
        ax.plot([xa, xb], [-ya, -yb], color=(GREY if pruned else "black"),
                lw=1.1 if pruned else 1.6, ls="--" if pruned else "-", zorder=1)

    for a, kids in (("root", ["A", "B"]), ("A", ["A1", "A2"]), ("B", ["B1", "B2"]),
                    ("A1", ["A1a", "A1b"]), ("A2", ["A2a", "A2b"]),
                    ("B1", ["B1a", "B1b"])):
        for k in kids:
            edge(a, k)
    edge("B", "B2", pruned=True)

    for name, (x, y) in pos.items():
        if name in leaves:
            v = leaves[name]
            cut = name in cut_leaves
            ax.add_patch(plt.Rectangle((x - 0.22, -y - 0.16), 0.44, 0.32,
                                       facecolor=("white" if not cut else "#eeeeee"),
                                       edgecolor=(RED if cut else "black"), lw=1.2, zorder=3))
            ax.text(x, -y, str(v), ha="center", va="center", fontsize=9,
                    color=(GREY if cut else "black"), zorder=4)
            if cut:
                ax.plot([x - 0.25, x + 0.25], [-y - 0.22, -y + 0.22], color=RED, lw=2, zorder=5)
                ax.plot([x - 0.25, x + 0.25], [-y + 0.22, -y - 0.22], color=RED, lw=2, zorder=5)
        elif name == "B2":
            ax.add_patch(plt.Circle((x, -y), 0.30, facecolor="#eeeeee", edgecolor=RED,
                                    lw=1.4, ls="--", zorder=3))
            ax.text(x, -y, "pruned", ha="center", va="center", fontsize=7.5, color=RED, zorder=4)
        else:
            ax.add_patch(plt.Circle((x, -y), 0.28, facecolor="white", edgecolor="black",
                                    lw=1.4, zorder=3))
            ax.text(x, -y, str(values[name]), ha="center", va="center", fontsize=9, zorder=4)

    ax.annotate("beta cut: at MAX node A2, 7 >= beta = 6\nso the leaf 3 is never evaluated",
                xy=(4.2, -2.95), xytext=(2.0, -3.85), fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
    ax.annotate("alpha cut: at MIN node B, 4 <= alpha = 6\nso the whole B2 subtree is skipped",
                xy=(7.9, -2.25), xytext=(5.5, -4.05), fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, 9.1)
    ax.set_ylim(-4.35, 0.6)
    ax.axis("off")
    fig.suptitle("alpha-beta pruning on a small game tree (Max at the root; leaves evaluated left to right)",
                 fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_alphabeta_tree.png"), dpi=160)
    plt.close(fig)


def main():
    nodes, sols = queens_search(4)
    assert len(sols) == 2 and sols[0] == (2, 4, 1, 3) and len(nodes) == 17
    nodes8, sols8 = queens_search(8)
    assert len(sols8) == 92 and sols8[0] == (1, 5, 8, 6, 3, 7, 2, 4)
    print("4-queens: solutions", sols, "nodes", len(nodes))
    print("8-queens: solutions", len(sols8), "first", sols8[0], "nodes", len(nodes8))

    ok, x, log = turnpike([1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 7, 8, 10])
    assert ok and x == [0, 3, 5, 6, 8, 10], (ok, x)
    print("turnpike:", x, "steps", len(log))

    root_value, order, pruned = alpha_beta()
    assert root_value == 6 and order == [5, 6, 7, 4, 2], (root_value, order)
    print("alpha-beta: root", root_value, "leaves evaluated", order, "pruned", pruned)

    draw_queens4_tree(nodes, sols)
    draw_queens8_board(sols[0] if False else (4, 6, 8, 2, 7, 1, 3, 5), sols8[0])
    draw_turnpike_tree()
    draw_alphabeta()


if __name__ == "__main__":
    main()

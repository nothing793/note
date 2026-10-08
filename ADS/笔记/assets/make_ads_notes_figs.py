# -*- coding: utf-8 -*-
"""生成 ADS 笔记中的示意图（自绘，非讲义截图）。
图均以英文标注，避免中文字体缺失导致的方框。
运行：python3 make_ads_notes_figs.py
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------- 图 1 二项队列
def binomial_children(k):
    """B_k 的根的孩子依次是 B_{k-1}, ..., B_0。"""
    return [k - 1 - i for i in range(k)]


def build_binomial(k):
    return {"k": k, "children": [build_binomial(j) for j in binomial_children(k)]}


def layout(node, depth=0, slots=[0]):
    """给叶子分配连续 y 槽位，内部节点取孩子均值。"""
    node["x"] = depth
    if not node["children"]:
        node["y"] = slots[0]
        slots[0] += 1
    else:
        ys = [layout(c, depth + 1, slots) for c in node["children"]]
        node["y"] = sum(ys) / len(ys)
    return node["y"]


def draw_binomial(ax, node, dx=1.0, dy=1.0, depth_zero=None):
    if depth_zero is None:
        depth_zero = node
    for c in node["children"]:
        ax.plot([node["x"] * dx, c["x"] * dx], [node["y"] * dy, c["y"] * dy],
                color="#333333", lw=1.0, zorder=1)
        draw_binomial(ax, c, dx, dy, depth_zero)
    ax.scatter([node["x"] * dx], [node["y"] * dy], s=150, facecolor="white",
               edgecolor="#333333", zorder=2)
    if depth_zero is node:
        ax.text(node["x"] * dx - 0.16, node["y"] * dy, "root",
                ha="right", va="center", fontsize=8, color="#b03030", zorder=3)


def fig_binomial_queue(path):
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.2))
    for ax, k in zip(axes, (0, 1, 2, 3)):
        tree = build_binomial(k)
        layout(tree, 0, [0])
        draw_binomial(ax, tree, depth_zero=tree)
        ax.set_title("$B_{%d}$  (nodes $=2^{%d}=%d$)" % (k, k, 2 ** k), fontsize=11)
        ax.axis("off")
    fig.suptitle(r"Binomial trees: $B_k$ = root with children $B_{k-1},\dots,B_0$;"
                 r"  #nodes at depth $d$ is $\binom{k}{d}$", fontsize=11, y=1.02)
    fig.text(0.5, -0.06,
             r"A queue of size 13 is $13=1101_2$, i.e. exactly $B_0+B_2+B_3$ "
             r"(one tree per height) -- self-made figure",
             ha="center", fontsize=10, color="#444444")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 图 2 Huffman
def fig_huffman_tree(path):
    # 频数来自讲义：a 10, e 15, i 12, s 3, t 4, sp 13, nl 1
    nodes = {
        "X":  dict(label="4",  children=["nl", "s"],  weight=4),
        "Y":  dict(label="8",  children=["t", "X"],   weight=8),
        "Z":  dict(label="18", children=["Y", "a"],   weight=18),
        "W":  dict(label="25", children=["i", "sp"],  weight=25),
        "V":  dict(label="33", children=["e", "Z"],   weight=33),
        "R":  dict(label="58", children=["W", "V"],   weight=58),
    }
    leaves = {"nl": ("nl:1", 1), "s": ("s:3", 3), "t": ("t:4", 4),
              "a": ("a:10", 10), "i": ("i:12", 12), "sp": ("sp:13", 13),
              "e": ("e:15", 15)}

    pos = {}

    def layout(name, depth, slot=[0.0]):
        if name in leaves:
            y = slot[0]
            slot[0] += 1
        else:
            ys = [layout(c, depth + 1, slot) for c in nodes[name]["children"]]
            y = sum(ys) / len(ys)
        pos[name] = (depth, y)
        return y

    layout("R", 0, [0.0])
    fig, ax = plt.subplots(figsize=(9, 5.0))
    for name, nd in nodes.items():
        for i, c in enumerate(nd["children"]):
            x0, y0 = pos[name]
            x1, y1 = pos[c]
            ax.plot([x0, x1], [y0, y1], color="#333", lw=1.2)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.12, str(i),
                    fontsize=11, color="#b03030", ha="center")
    for name, nd in nodes.items():
        x, y = pos[name]
        ax.scatter([x], [y], s=420, facecolor="#f2f2f2", edgecolor="#333", zorder=3)
        ax.text(x, y, nd["label"], ha="center", va="center", fontsize=9, zorder=4)
    for name, (lab, w) in leaves.items():
        x, y = pos[name]
        ax.scatter([x], [y], s=520, facecolor="#ffffff", edgecolor="#333", zorder=3)
        ax.text(x, y, lab, ha="center", va="center", fontsize=9, zorder=4)
        ax.text(x, y - 0.42, "depth %d" % int(round(x)), ha="center",
                fontsize=8, color="#555")
    ax.set_ylim(-1.0, max(y for _, y in pos.values()) + 0.35)
    ax.axis("off")
    ax.set_title("Huffman tree for the slide's frequencies "
                 "(a 10, e 15, i 12, s 3, t 4, sp 13, nl 1)", fontsize=11)
    fig.text(0.5, -0.02,
             "Cost = 3*10 + 2*15 + 2*12 + 5*3 + 4*4 + 2*13 + 5*1 = 146  "
             "(matches the slide) -- self-made figure",
             ha="center", fontsize=9, color="#444")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 图 3 strip
def fig_closest_strip(path):
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    d = 1.0                      # δ
    ax.add_patch(Rectangle((-d, -0.6), 2 * d, 1.2, fill=False,
                           edgecolor="#888", linestyle="--", lw=1.0))
    ax.text(-d - 0.03, 0.66, "strip width 2$\\delta$", fontsize=9, color="#666")
    ax.axvline(0, color="#333", lw=1.2, linestyle="--")
    ax.text(0.02, 0.72, "dividing line", fontsize=9, color="#333")
    # 右侧 2δ(宽) × δ(高) 矩形，切成 4 × 2 个边长 δ/2 的小方格
    ax.add_patch(Rectangle((0, -d / 2), 2 * d, d, facecolor="#eef4ff",
                           edgecolor="#4a6fa5", lw=1.2))
    for i in range(1, 4):
        ax.plot([i * d / 2, i * d / 2], [-d / 2, d / 2], color="#4a6fa5", lw=0.8)
    ax.plot([0, 2 * d], [0, 0], color="#4a6fa5", lw=0.8)
    ax.annotate("", xy=(2 * d, -d / 2 - 0.12), xytext=(0, -d / 2 - 0.12),
                arrowprops=dict(arrowstyle="<->", color="#4a6fa5"))
    ax.text(d, -d / 2 - 0.22, "2$\\delta$", ha="center", fontsize=10, color="#4a6fa5")
    ax.annotate("", xy=(2 * d + 0.1, d / 2), xytext=(2 * d + 0.1, -d / 2),
                arrowprops=dict(arrowstyle="<->", color="#4a6fa5"))
    ax.text(2 * d + 0.14, 0, "$\\delta$", va="center", fontsize=10, color="#4a6fa5")
    ax.text(d / 2, d / 2 - 0.18, "$\\delta/2$", fontsize=9, color="#4a6fa5")
    ax.scatter([0], [0], s=90, color="#c03030", zorder=5)
    ax.text(-0.06, -0.12, "$p_i$", fontsize=12, color="#c03030", ha="right")
    ax.text(2 * d + 0.12, 0.55,
            "8 cells of side $\\delta/2$:\n"
            "each cell holds at most one point\n"
            "(two points in one cell would be\n"
            "$<\\delta$ apart)  $\\Rightarrow$  at most 7\n"
            "other points to compare with $p_i$",
            fontsize=9.5, va="top", color="#333")
    ax.set_xlim(-d - 0.2, 2 * d + 1.5)
    ax.set_ylim(-0.9, 0.95)
    ax.axis("off")
    ax.set_title("Closest pair: why the strip costs only $O(N)$ -- self-made figure",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- 图 4 外部排序
def fig_external_sort(path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2),
                                   gridspec_kw={"width_ratios": [1.35, 1]})
    # 左：多趟归并（8 run -> 4 -> 2 -> 1）
    levels = [(8, "8 runs"), (4, "4 runs"), (2, "2 runs"), (1, "1 run")]
    for li, (cnt, lab) in enumerate(levels):
        y = -li
        for i in range(cnt):
            x = (i + 0.5) * (8.0 / cnt)
            ax1.add_patch(Rectangle((x - 8.0 / cnt / 2 + 0.06, y - 0.22),
                                    8.0 / cnt - 0.12, 0.44,
                                    facecolor="#eef4ff", edgecolor="#4a6fa5", lw=1.0))
        ax1.text(-0.35, y, lab, ha="right", va="center", fontsize=9.5, color="#333")
    for li in range(3):
        cnt = 8 >> li
        nxt = cnt // 2
        for i in range(nxt):
            x0 = (2 * i + 1) * (8.0 / cnt)
            x1 = (i + 0.5) * (8.0 / nxt)
            ax1.plot([x0, x1], [-li - 0.24, -li - 0.76], color="#888", lw=0.8)
            x0b = (2 * i + 2) * (8.0 / cnt)
            ax1.plot([x0b, x1], [-li - 0.24, -li - 0.76], color="#888", lw=0.8)
    ax1.text(4, -3.55, "passes = 1 (run generation) + $\\lceil\\log_2 8\\rceil$ = 4 -- self-made figure",
             ha="center", fontsize=9.5, color="#444")
    ax1.set_xlim(-2.4, 8.4)
    ax1.set_ylim(-3.9, 0.6)
    ax1.axis("off")
    ax1.set_title("Multi-pass merging (2-way merge)", fontsize=11)

    # 右：R = 320 runs 时，趟数随 k 变化
    R = 320
    ks = list(range(2, 17))
    passes = [1 + math.ceil(math.log(R, k)) for k in ks]
    bars = ax2.bar([str(k) for k in ks], passes, color="#4a6fa5", alpha=0.85)
    for k, p, b in zip(ks, passes, bars):
        ax2.text(b.get_x() + b.get_width() / 2, p + 0.12, str(p),
                 ha="center", fontsize=8.5, color="#333")
    ax2.set_xlabel("k (k-way merge)", fontsize=10)
    ax2.set_ylabel("number of passes", fontsize=10)
    ax2.set_title("passes = $1+\\lceil\\log_k R\\rceil$ with $R=320$ runs",
                  fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_binomial_queue("fig_binomial_queue.png")
    fig_huffman_tree("fig_huffman_tree.png")
    fig_closest_strip("fig_closest_strip.png")
    fig_external_sort("fig_external_sort.png")
    print("done")

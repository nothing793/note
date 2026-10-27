# -*- coding: utf-8 -*-
"""ADS07 分治法与递归式的自绘示意图。

图均以英文标注（避免中文字体缺失时出现方框），中文说明写在笔记图注里。
运行：python3 make_ads07_figs.py   （图片写在脚本所在目录）

- fig_closest_pair_demo.png : 最近点对：左右递归 + 宽度 2δ 的 strip + 跨界最近点对
- fig_closest_packing.png   : 7 点引理的 4×2 网格证明
- fig_recursion_trees.png   : 三种典型递归式的递归树（平衡 / 几何衰减 / 不平衡）

最近点对图中的 δ_L、δ_R、δ 与高亮线段都由脚本真算得到（末尾有断言）。
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["axes.unicode_minus"] = False
HERE = os.path.dirname(os.path.abspath(__file__))

BLUE = "#1f5fa8"
GREEN = "#1e8449"
RED = "#c0392b"
GREY = "#8a8a8a"


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def closest_within(points):
    if len(points) < 2:
        return math.inf, None
    best = math.inf
    pair = None
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = dist(points[i], points[j])
            if d < best:
                best, pair = d, (points[i], points[j])
    return best, pair


def fig_closest_pair_demo(path):
    left = [(1.0, 1.0), (2.5, 5.0), (3.0, 2.0),
            (4.5, 3.0), (2.0, 6.0), (3.5, 4.5)]
    right = [(5.5, 3.0), (7.0, 5.0), (8.0, 1.0),
             (9.0, 4.0), (6.5, 2.0), (8.5, 6.0)]
    split = 5.0
    dL, _ = closest_within(left)
    dR, _ = closest_within(right)
    delta = min(dL, dR)
    cross, cross_pair = closest_within(left + right)
    assert abs(cross - 1.0) < 1e-12
    assert cross_pair[0] in left and cross_pair[1] in right
    assert cross < delta

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.add_patch(Rectangle((split - delta, -0.4), 2 * delta, 7.2,
                           facecolor="#fff3cd", edgecolor="#c9a227",
                           alpha=0.55, zorder=0))
    ax.axvline(split, color="#333333", lw=1.2, ls="--", zorder=1)
    ax.text(split + 0.06, 6.75, "dividing line", fontsize=9, color="#333333")

    ax.scatter([p[0] for p in left], [p[1] for p in left],
               s=70, color=BLUE, label="left half", zorder=3)
    ax.scatter([p[0] for p in right], [p[1] for p in right],
               s=70, color=GREEN, label="right half", zorder=3)

    a, b = cross_pair
    ax.plot([a[0], b[0]], [a[1], b[1]], color=RED, lw=2.8, zorder=4)
    ax.scatter([a[0], b[0]], [a[1], b[1]], s=130, facecolor="white",
               edgecolor=RED, linewidth=2.0, zorder=5)
    ax.annotate("cross pair: distance 1.000\n(the combine step must find it)",
                xy=((a[0] + b[0]) / 2, a[1]), xytext=(6.0, 1.05),
                fontsize=8.6, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))

    ax.annotate("", xy=(split - delta, 0.05), xytext=(split + delta, 0.05),
                arrowprops=dict(arrowstyle="<->", color="#c9a227", lw=1.2))
    ax.text(split + 0.65, -0.28, r"strip width $2\delta=%.3f$" % (2 * delta),
            ha="left", fontsize=9, color="#8a6d00",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.text(0.35, 6.55, r"$\delta_L=%.3f$" % dL, fontsize=10, color=BLUE)
    ax.text(6.5, 6.55, r"$\delta_R=%.3f$" % dR, fontsize=10, color=GREEN)
    ax.text(0.35, 6.15, r"$\delta=\min(\delta_L,\delta_R)=%.3f$" % delta,
            fontsize=10, color="#333333")

    ax.set_xlim(0.3, 10.3)
    ax.set_ylim(-0.5, 7.0)
    ax.set_aspect("equal")
    ax.set_xlabel("x", fontsize=10)
    ax.set_ylabel("y", fontsize=10)
    ax.legend(loc="lower right", fontsize=9, frameon=True)
    ax.set_title("Closest pair: solve halves recursively, then scan the strip",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_closest_packing(path):
    d = 1.0
    fig, ax = plt.subplots(figsize=(7.8, 4.3))
    ax.add_patch(Rectangle((-d, 0), 2 * d, d, facecolor="#eef4ff",
                           edgecolor="#4a6fa5", lw=1.4, zorder=1))
    for i in range(1, 4):
        ax.plot([-d + i * d / 2, -d + i * d / 2], [0, d],
                color="#4a6fa5", lw=0.9, zorder=2)
    ax.plot([-d, d], [d / 2, d / 2], color="#4a6fa5", lw=0.9, zorder=2)
    ax.axvline(0, color="#333333", lw=1.5, ls="--", zorder=3)
    ax.text(0.03, d + 0.06, "dividing line", fontsize=9, color="#333333")

    ax.add_patch(Rectangle((-d, 0), d, d, facecolor=BLUE, alpha=0.08,
                           edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, 0), d, d, facecolor=GREEN, alpha=0.08,
                           edgecolor="none", zorder=0))

    ax.scatter([-0.36], [0.0], s=110, color=RED, zorder=5, clip_on=False)
    ax.text(-0.40, -0.10, r"$p$", fontsize=13, color=RED, ha="right")

    ax.annotate("", xy=(-d, -0.12), xytext=(d, -0.12),
                arrowprops=dict(arrowstyle="<->", color="#4a6fa5"))
    ax.text(0.55, -0.27, r"$2\delta$", ha="center", fontsize=11, color="#4a6fa5",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("", xy=(-d - 0.12, 0), xytext=(-d - 0.12, d),
                arrowprops=dict(arrowstyle="<->", color="#4a6fa5"))
    ax.text(-d - 0.17, d / 2, r"$\delta$", va="center", ha="right",
            fontsize=11, color="#4a6fa5")
    ax.text(-d + d / 4, d / 2 - 0.07, r"$\delta/2$", ha="center",
            fontsize=9, color="#4a6fa5")

    ax.text(1.12, 0.78,
            "4 columns x 2 rows = 8 cells\n"
            "each cell lies wholly in one half\n"
            "=> at most one point per cell\n"
            "=> at most 8 points including p\n"
            "=> compare p with at most 7 others",
            fontsize=9.2, va="top", color="#333333")
    ax.set_xlim(-d - 0.35, 2.55)
    ax.set_ylim(-0.35, d + 0.28)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Packing lemma: why only the next 7 points need checking",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _node(ax, x, y, text, color="#333333", size=8.5, s=760):
    ax.scatter([x], [y], s=s, facecolor="white", edgecolor=color,
               linewidth=1.4, zorder=3)
    ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=4)


def _edge(ax, x0, y0, x1, y1, color=GREY):
    ax.plot([x0, x1], [y0, y1], color=color, lw=1.1, zorder=1)


def fig_recursion_trees(path):
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4))

    ax = axes[0]
    xs = {0: [0.0], 1: [-0.9, 0.9], 2: [-1.35, -0.45, 0.45, 1.35]}
    ys = {0: 0.0, 1: -1.0, 2: -2.0}
    labels = {0: [r"$n$"], 1: [r"$n/2$"] * 2, 2: [r"$n/4$"] * 4}
    for lev in (1, 2):
        for i, x in enumerate(xs[lev]):
            parent = xs[lev - 1][i // 2]
            _edge(ax, parent, ys[lev - 1], x, ys[lev], BLUE)
    for lev in (0, 1, 2):
        for x, lab in zip(xs[lev], labels[lev]):
            _node(ax, x, ys[lev], lab, BLUE, 7.2)
    ax.text(1.75, -0.1, r"level cost $=n$", fontsize=9, color=BLUE)
    ax.text(1.75, -1.1, r"$=n$", fontsize=9, color=BLUE)
    ax.text(1.75, -2.1, r"$=n$", fontsize=9, color=BLUE)
    ax.text(0, -2.85, r"$T(n)=2T(n/2)+n=\Theta(n\log n)$",
            ha="center", fontsize=9.5)
    ax.set_title("(a) balanced, per-level cost constant", fontsize=10)
    ax.set_xlim(-1.8, 2.6)
    ax.set_ylim(-3.2, 0.5)
    ax.axis("off")

    ax = axes[1]
    xs = {0: [0.0], 1: [-1.0, 0.0, 1.0]}
    for x in xs[1]:
        _edge(ax, 0.0, 0.0, x, -1.0, GREEN)
    _node(ax, 0.0, 0.0, r"$n^2$", GREEN)
    for x in xs[1]:
        _node(ax, x, -1.0, r"$\frac{n^2}{16}$", GREEN, 7.0)
    for x in xs[1]:
        for dx in (-0.18, 0.18):
            _edge(ax, x, -1.0, x + dx, -1.85, GREEN)
            _node(ax, x + dx, -1.85, r"$\frac{n^2}{256}$", GREEN, 5.0, 390)
    ax.text(1.55, -0.05, r"$n^2$", fontsize=9, color=GREEN)
    ax.text(1.55, -1.05, r"$\frac{3}{16}n^2$", fontsize=9, color=GREEN)
    ax.text(1.55, -1.90, r"$\left(\frac{3}{16}\right)^2n^2$",
            fontsize=9, color=GREEN)
    ax.text(0, -2.85,
            r"$T(n)=3T(n/4)+n^2=\Theta(n^2)$  (geometric decay)",
            ha="center", fontsize=9.5)
    ax.set_title("(b) combine dominates", fontsize=10)
    ax.set_xlim(-1.8, 2.4)
    ax.set_ylim(-3.2, 0.5)
    ax.axis("off")

    ax = axes[2]
    pos = {
        0: (0.0, 0.0, r"$n$"),
        1: (-1.0, -1.0, r"$n/3$"),
        2: (1.0, -1.0, r"$2n/3$"),
        3: (-1.35, -2.0, r"$n/9$"),
        4: (-0.55, -2.0, r"$2n/9$"),
        5: (0.55, -2.0, r"$2n/9$"),
        6: (1.35, -2.0, r"$4n/9$"),
    }
    for a, b in ((0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)):
        _edge(ax, pos[a][0], pos[a][1], pos[b][0], pos[b][1], RED)
    for x, y, lab in pos.values():
        _node(ax, x, y, lab, RED, 7.0)
    ax.text(1.72, -0.05, r"level sum $=n$", fontsize=9, color=RED)
    ax.text(1.72, -1.05, r"$=n$", fontsize=9, color=RED)
    ax.text(0, -2.85,
            r"$T(n)=T(n/3)+T(2n/3)+n=\Theta(n\log n)$",
            ha="center", fontsize=9.5)
    ax.set_title("(c) unbalanced, depth differs by a constant factor",
                 fontsize=10)
    ax.set_xlim(-1.8, 2.6)
    ax.set_ylim(-3.2, 0.5)
    ax.axis("off")

    fig.suptitle("Recursion trees: sum the cost level by level (self-made figure)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_closest_pair_demo(os.path.join(HERE, "fig_closest_pair_demo.png"))
    fig_closest_packing(os.path.join(HERE, "fig_closest_packing.png"))
    fig_recursion_trees(os.path.join(HERE, "fig_recursion_trees.png"))
    print("done")

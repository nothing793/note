# -*- coding: utf-8 -*-
"""ADS08 动态规划的自绘示意图。

运行：python3 make_ads08_figs.py   （图片写在脚本所在目录）

- fig_dp_interval_order.png : 矩阵连乘的区间 DP 填表顺序
  * 行 i、列 j 只填 j >= i 的上三角；
  * 长度 len = j - i + 1 从 2 增到 N；
  * 每个格子只依赖更短区间，所以按长度递增一定没有循环依赖。

图中的 m[i][j] 由脚本用讲义例子
M1[10x20] M2[20x50] M3[50x1] M4[1x100]
真实计算得到，并在末尾断言 m[0][3] == 2200。
"""
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
GREY = "#777777"


def matrix_chain(r):
    """r[i-1] x r[i] is the shape of matrix i; returns m and split tables."""
    n = len(r) - 1
    inf = float("inf")
    m = [[0] * n for _ in range(n)]
    split = [[-1] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            m[i][j] = inf
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + r[i] * r[k + 1] * r[j + 1]
                if cost < m[i][j]:
                    m[i][j] = cost
                    split[i][j] = k
    return m, split


def fig_interval_order(path):
    r = [10, 20, 50, 1, 100]
    m, split = matrix_chain(r)
    assert m[0][3] == 2200
    assert split[0][3] == 2

    n = 4
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    colors = {
        1: "#f2f2f2",
        2: "#dbe9f6",
        3: "#b8d4ee",
        4: "#8dbbdf",
    }
    for i in range(n):
        for j in range(n):
            if j < i:
                continue
            length = j - i + 1
            rect = Rectangle((j, n - 1 - i), 1, 1,
                             facecolor=colors[length],
                             edgecolor="white", linewidth=2.0, zorder=1)
            ax.add_patch(rect)
            text = f"{m[i][j]:,}" if length >= 2 else "0"
            ax.text(j + 0.5, n - 1 - i + 0.5, text,
                    ha="center", va="center", fontsize=10.5,
                    color="#222222", zorder=2)
            if length >= 2:
                ax.text(j + 0.12, n - 1 - i + 0.12,
                        f"len={length}", fontsize=6.8, color=GREY, zorder=2)

    # 行、列标签
    for i in range(n):
        ax.text(-0.18, n - 0.5 - i, f"$i={i+1}$", ha="right", va="center",
                fontsize=10)
    for j in range(n):
        ax.text(j + 0.5, n + 0.10, f"$j={j+1}$", ha="center", va="bottom",
                fontsize=10)

    # 高亮最优值
    ax.add_patch(Rectangle((3.02, n - 1.02), 0.96, 0.96,
                           fill=False, edgecolor=RED, linewidth=2.4,
                           zorder=5))
    ax.annotate("optimal cost 2,200\nsplit after $M_3$",
                xy=(3.5, n - 0.55), xytext=(4.25, n - 1.55),
                fontsize=9.0, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))

    ax.text(0.0, -0.85,
            r"$m[i][j]=\min_{i\leq k<j}"
            r"\left(m[i][k]+m[k+1][j]+r_{i-1}r_k r_j\right)$"
            "\n"
            "fill order: $len=2,3,\\ldots,N$ (short intervals first)",
            fontsize=9.5, color="#222222", va="top")
    ax.text(0.0, -1.65,
            "colors show interval length; every cell only depends on shorter intervals",
            fontsize=8.6, color=GREY, va="top")

    ax.set_xlim(-0.55, 7.0)
    ax.set_ylim(-1.85, n + 0.55)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Matrix-chain DP: triangular table filled by interval length",
                 fontsize=11.5)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    fig_interval_order(os.path.join(HERE, "fig_dp_interval_order.png"))
    print("wrote fig_dp_interval_order.png")


if __name__ == "__main__":
    main()

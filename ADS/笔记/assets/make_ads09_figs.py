# -*- coding: utf-8 -*-
"""ADS09 贪心算法的自绘示意图。

运行：python3 make_ads09_figs.py   （图片写在脚本所在目录）

- fig_activity_selection.png：讲义 11 个活动的区间图。
  绿色是按“最早结束时间”选出的相容活动 {a1, a4, a8, a11}，共 4 个；
  灰色是未被选中的活动。脚本只画图，不重新实现算法；
  选出的下标与讲义例子一致（a1 [1,4), a4 [5,7), a8 [8,11), a11 [12,16)）。
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["axes.unicode_minus"] = False
HERE = os.path.dirname(os.path.abspath(__file__))

ACTS = [
    (1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
    (6, 10), (8, 11), (8, 12), (2, 14), (12, 16),
]
CHOSEN = {1, 4, 8, 11}

GREEN = "#1e8449"
GREY = "#b8c4d6"


def fig_activity_selection(path):
    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    n = len(ACTS)
    for i, (s, f) in enumerate(ACTS, start=1):
        y = n - i
        color = GREEN if i in CHOSEN else GREY
        ax.add_patch(Rectangle((s, y - 0.32), f - s, 0.64,
                               facecolor=color, edgecolor="#333333",
                               linewidth=0.8, zorder=2))
        ax.text(s - 0.25, y, f"$a_{i}$", ha="right", va="center",
                fontsize=9.5, color="#222222")
        ax.text(f + 0.2, y, f"[{s},{f})", ha="left", va="center",
                fontsize=7.5, color="#555555")
    ax.set_xlim(-1.4, 18.6)
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_yticks([])
    ax.set_xlabel("time", fontsize=10)
    ax.set_title("Activity selection: earliest finish first (green = chosen)",
                 fontsize=11)
    ax.grid(axis="x", linestyle=":", color="#cccccc", zorder=0)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, path), dpi=160, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_activity_selection("fig_activity_selection.png")

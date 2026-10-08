#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the schematic figures used in ADS/笔记/02_ADS001_伸展树与摊还分析.md.

Why everything in the figures is Latin/mathtext: the only CJK font installed on
this machine (Droid Sans Fallback) contains no Latin glyphs, so a mixed CN/EN
label would come out as empty boxes.  All Chinese explanation lives in the
markdown around each figure.

Run:  python3 make_avl_figs.py      (writes fig_*.png next to this file)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["axes.unicode_minus"] = False

BLUE_F, BLUE_E = "#dbeafe", "#1e3a8a"      # ordinary node
RED_F,  RED_E = "#fecaca", "#b91c1c"       # unbalanced node (trouble finder)
WRN_F,  WRN_E = "#fed7aa", "#c2410c"       # higher ancestor, needs no fixing
GRN_F,  GRN_E = "#bbf7d0", "#15803d"       # newly inserted / subtree that grew
BOX_F,  BOX_E = "#fef9c3", "#a16207"       # a subtree collapsed into one box
DX, DY = 1.55, 1.30                        # spacing between nodes
R, BW, BH = 0.30, 1.02, 0.58               # radius / box size


class N:
    def __init__(self, label, left=None, right=None, box=False,
                 style="normal", h=None, bf=None):
        self.label, self.left, self.right = str(label), left, right
        self.box, self.style, self.h, self.bf = box, style, h, bf


def layout(root, dx):
    cnt = [0]

    def walk(n, d):
        if n is None:
            return
        walk(n.left, d + 1)
        n.x, n.y = cnt[0] * dx, -d * DY
        cnt[0] += 1
        walk(n.right, d + 1)

    walk(root, 0)


def draw(ax, root, title, caption, ylim, xspan, dx):
    layout(root, dx)
    xs, ys = [], []

    def edges(n):
        for c in (n.left, n.right):
            if c is None:
                continue
            ax.plot([n.x, c.x], [n.y, c.y], color="#64748b", lw=1.3, zorder=1)
            edges(c)

    def shapes(n):
        if n.box:
            fc, ec = (GRN_F, GRN_E) if n.style == "new" else (BOX_F, BOX_E)
            ax.add_patch(FancyBboxPatch((n.x - BW / 2, n.y - BH / 2), BW, BH,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        fc=fc, ec=ec, lw=1.2, zorder=2))
            gap = BW / 2 + 0.12
        else:
            fc, ec = {"normal": (BLUE_F, BLUE_E), "bad": (RED_F, RED_E),
                      "warn": (WRN_F, WRN_E), "new": (GRN_F, GRN_E)}[n.style]
            rr = R + 0.105 * max(0, len(n.label) - 1)
            ax.add_patch(Circle((n.x, n.y), rr, fc=fc, ec=ec, lw=1.7, zorder=2))
            gap = rr + 0.08
        ax.text(n.x, n.y, n.label, ha="center", va="center",
                fontsize=(11 if len(n.label) < 2 else 9.5),
                color="#111827", zorder=3)
        if n.h is not None:                       # subtree height
            ax.text(n.x - gap, n.y, n.h, ha="right", va="center", fontsize=9,
                    color="#1d4ed8", zorder=3)
        if n.bf is not None:                      # balance factor
            ax.text(n.x + gap, n.y, n.bf, ha="left", va="center", fontsize=9,
                    color="#b91c1c", zorder=3)
        xs.append(n.x); ys.append(n.y)
        for c in (n.left, n.right):
            if c is not None:
                shapes(c)

    edges(root)
    shapes(root)
    xc = (min(xs) + max(xs)) / 2
    ax.set_aspect("equal")
    ax.set_xlim(xc - xspan / 2, xc + xspan / 2)
    ax.set_ylim(*ylim)
    ax.set_anchor("N")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11.5, color="#0f172a", pad=10)
    if caption:
        ax.text(xc, ylim[0] + 0.10, caption, ha="center", va="bottom",
                fontsize=9.5, color="#334155", linespacing=1.5)


def extents(panels, dx):
    xs, ys = [], []
    for p in panels:
        layout(p["root"], dx)
        stack = [p["root"]]
        while stack:
            n = stack.pop()
            xs.append(n.x); ys.append(n.y)
            stack += [c for c in (n.left, n.right) if c is not None]
    return xs, ys


def save(panels, path, width=10.0, ncols=None, dx=DX, extra_h=1.2):
    """Grid layout; the figure height follows from the content so that all
    panels share one scale and no big empty area is left."""
    ncols = len(panels) if ncols is None else ncols
    nrows = -(-len(panels) // ncols)
    xs, ys = extents(panels, dx)
    xspan = (max(xs) - min(xs)) + 2.6
    panel_w = width / ncols
    upin = xspan / panel_w                      # data units per inch
    lines = max((len(p["caption"].split("\n")) if p.get("caption") else 0)
                for p in panels)
    reserve = lines * (9.5 / 72) * upin * 1.5 + 0.30   # room for the caption
    ylim = (min(ys) - 1.05 - reserve, max(ys) + 1.05)
    yspan = ylim[1] - ylim[0]
    height = nrows * (panel_w * yspan / xspan + extra_h)
    fig, axes = plt.subplots(nrows, ncols, figsize=(width, height), squeeze=False)
    axes = [ax for row in axes for ax in row]
    for k, ax in enumerate(axes):
        if k < len(panels):
            p = panels[k]
            draw(ax, p["root"], p.get("title"), p.get("caption"),
                 ylim, xspan, dx)
        else:
            ax.axis("off")
    fig.tight_layout(pad=0.6)
    # 输出固定写到脚本所在目录，避免受当前工作目录（cwd）影响
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        os.path.basename(path))
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print("wrote", path, flush=True)


def box(l, h=None, style="normal"):
    return N(l, box=True, h=h, style=style)


def node(l, left=None, right=None, style="normal", h=None, bf=None):
    return N(l, left, right, style=style, h=h, bf=bf)


# ---------------------------------------------------------------------------
def fig_search():
    complete = node(6, node(3, node(2, node(1)), node(5, node(4))),
                    node(9, node(8, node(7)), node(11, node(10), node(12))))
    skew = None
    for v in range(12, 0, -1):
        skew = node(v, None, skew)
    save([{"root": complete, "title": "Complete tree, n = 12",
           "caption": "$IPL = 0+2+8+15 = 25$\n$ASL = 25/12 + 1 \\approx 3.1$"},
          {"root": skew, "title": "Skew tree (1, 2, ..., 12)",
           "caption": "$IPL = 0+1+\\cdots+11 = 66$\n$ASL = 66/12 + 1 = 6.5$"}],
         "fig_search_asl.png", width=10.0)


def fig_single_rotation():
    save([{"root": node("A", None, node("B", box("X"), box("Y"))),
           "title": "Left rotation: before", "caption": "rotate at $A$"},
          {"root": node("B", node("A", box("X"), box("Y")), box("Z")),
           "title": "Left rotation: after",
           "caption": "inorder  $X < A < Y < B < Z$"},
          {"root": node("A", node("B", box("X"), box("Y")), None),
           "title": "Right rotation: before", "caption": "rotate at $A$"},
          {"root": node("B", box("Z"), node("A", box("X"), box("Y"))),
           "title": "Right rotation: after",
           "caption": "inorder  $X < B < Y < A < Z$"}],
         "fig_rotation_single.png", width=10.6, ncols=2)


def fig_ll():
    before = node("A", node("B", box("$T_{h+1}$", "$h{+}1$", style="new"),
                            box("$T_h$", "$h$"), h="$h{+}2$", bf="bf=+1"),
                  box("$T_h$", "$h$"), style="bad", h="$h{+}3$", bf="bf=+2")
    after = node("B", box("$T_{h+1}$", "$h{+}1$", style="new"),
                 node("A", box("$T_h$", "$h$"), box("$T_h$", "$h$"),
                      h="$h{+}1$", bf="bf=0"), h="$h{+}2$", bf="bf=0")
    save([{"root": before, "title": "LL case: bf(A) = +2",
           "caption": "right rotation at $A$"},
          {"root": after, "title": "After the rotation",
           "caption": "height back to $h+2$"}],
         "fig_avl_ll.png", width=9.6)


def fig_rr():
    before = node("A", box("$T_h$", "$h$"),
                  node("B", box("$T_h$", "$h$"),
                       box("$T_{h+1}$", "$h{+}1$", style="new"),
                       h="$h{+}2$", bf="bf=-1"),
                  style="bad", h="$h{+}3$", bf="bf=-2")
    after = node("B", node("A", box("$T_h$", "$h$"), box("$T_h$", "$h$"),
                           h="$h{+}1$", bf="bf=0"),
                 box("$T_{h+1}$", "$h{+}1$", style="new"),
                 h="$h{+}2$", bf="bf=0")
    save([{"root": before, "title": "RR case: bf(A) = -2",
           "caption": "left rotation at $A$"},
          {"root": after, "title": "After the rotation",
           "caption": "mirror image of LL"}],
         "fig_avl_rr.png", width=9.6)


def fig_lr():
    p1 = node("A", node("B", box("$T_1$", "$h$"),
                        node("C", box("$T_2$", "$h$"), box("$T_3$", "$h$"),
                             style="new", h="$h{+}1$", bf="bf=0"),
                        h="$h{+}2$", bf="bf=-1"),
              box("$T_4$", "$h$"), style="bad", h="$h{+}3$", bf="bf=+2")
    p2 = node("A", node("C", node("B", box("$T_1$", "$h$"), box("$T_2$", "$h$"),
                                   h="$h{+}1$", bf="bf=0"),
                        box("$T_3$", "$h$"), h="$h{+}2$", bf="bf=+1"),
              box("$T_4$", "$h$"), style="bad", h="$h{+}3$", bf="bf=+2")
    p3 = node("C", node("B", box("$T_1$", "$h$"), box("$T_2$", "$h$"),
                        h="$h{+}1$", bf="bf=0"),
              node("A", box("$T_3$", "$h$"), box("$T_4$", "$h$"),
                   h="$h{+}1$", bf="bf=0"), h="$h{+}2$", bf="bf=0")
    save([{"root": p1, "title": "LR case:  bf(A) = +2,  bf(B) = -1",
           "caption": "green $C$: the subtree that grew"},
          {"root": p2, "title": "Step 1: left rotation at $B$",
           "caption": "now an LL shape"},
          {"root": p3, "title": "Step 2: right rotation at $A$",
           "caption": "balanced again"}],
         "fig_avl_lr.png", width=10.0, ncols=2)


def fig_rl():
    p1 = node("A", box("$T_1$", "$h$"),
              node("B", node("C", box("$T_2$", "$h$"), box("$T_3$", "$h$"),
                             style="new", h="$h{+}1$", bf="bf=0"),
                   box("$T_4$", "$h$"), h="$h{+}2$", bf="bf=+1"),
              style="bad", h="$h{+}3$", bf="bf=-2")
    p2 = node("A", box("$T_1$", "$h$"),
              node("C", box("$T_2$", "$h$"),
                   node("B", box("$T_3$", "$h$"), box("$T_4$", "$h$"),
                        h="$h{+}1$", bf="bf=0"), h="$h{+}2$", bf="bf=-1"),
              style="bad", h="$h{+}3$", bf="bf=-2")
    p3 = node("C", node("A", box("$T_1$", "$h$"), box("$T_2$", "$h$"),
                        h="$h{+}1$", bf="bf=0"),
              node("B", box("$T_3$", "$h$"), box("$T_4$", "$h$"),
                   h="$h{+}1$", bf="bf=0"), h="$h{+}2$", bf="bf=0")
    save([{"root": p1, "title": "RL case:  bf(A) = -2,  bf(B) = +1",
           "caption": "green $C$: the subtree that grew"},
          {"root": p2, "title": "Step 1: right rotation at $B$",
           "caption": "now an RR shape"},
          {"root": p3, "title": "Step 2: left rotation at $A$",
           "caption": "balanced again"}],
         "fig_avl_rl.png", width=10.0, ncols=2)


def fig_trouble():
    p1 = node("5", node("3", node("2", node("1", style="new"),
                                  style="new", bf="bf=+1"),
                        style="bad", bf="bf=+2"),
              node("8"), style="warn", bf="bf=+2")
    p2 = node("5", node("2", node("1", style="new"), node("3"), bf="bf=+1"),
              node("8"))
    save([{"root": p1, "title": "After inserting 1",
           "caption": "$bf = +2$ at 3 and at 5"},
          {"root": p2, "title": "Right rotation at 3 only",
           "caption": "5 is balanced again"}],
         "fig_avl_trouble.png", width=9.6)


def fig_nh():
    root = node("$h$", box("$T_{h-1}$"), box("$T_{h-2}$"))
    save([{"root": root, "title": None,
           "caption": "$T_k$: smallest AVL tree of height $k$\n"
                      "$n_h = n_{h-1}+n_{h-2}+1$,  $n_0=1$,  $n_1=2$\n"
                      "$\\Rightarrow n_h = F_{h+3}-1$\n"
                      "$\\Rightarrow h = O(\\log n)$"}],
         "fig_avl_nh.png", width=6.4, dx=2.7)


if __name__ == "__main__":
    for f in (fig_search, fig_single_rotation, fig_ll, fig_rr,
              fig_lr, fig_rl, fig_trouble, fig_nh):
        f()

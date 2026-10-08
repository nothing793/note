#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the splay-tree schematic figures used in ADS/笔记/02_ADS001_伸展树与摊还分析.md.

Same conventions as make_avl_figs.py: only Latin/mathtext labels inside the
figures (the only CJK font on this machine, Droid Sans Fallback, has no Latin
glyphs, so mixed CN/EN labels would render as boxes); all Chinese explanation
lives in the markdown around each figure.

The skew-tree panel is not hand-drawn: the trees in fig_splay_vs_single.png are
produced by actually running the two algorithms (rotate-to-root vs. splay) on
the chain 7-6-5-4-3-2-1, so the shapes are what the algorithms really return.

Run:  python3 make_splay_figs.py      (writes fig_splay_*.png next to this file)
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
RED_F,  RED_E = "#fecaca", "#b91c1c"       # node we are rotating about (x)
GRN_F,  GRN_E = "#bbf7d0", "#15803d"       # parent P / grandparent G
BOX_F,  BOX_E = "#fef9c3", "#a16207"       # a subtree collapsed into one box
DX, DY = 1.55, 1.30                        # spacing between nodes
R, BW, BH = 0.30, 1.02, 0.58               # radius / box size


class N:
    def __init__(self, label, left=None, right=None, box=False,
                 style="normal", note=None):
        self.label, self.left, self.right = str(label), left, right
        self.box, self.style, self.note = box, style, note


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
            ax.add_patch(FancyBboxPatch((n.x - BW / 2, n.y - BH / 2), BW, BH,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        fc=BOX_F, ec=BOX_E, lw=1.2, zorder=2))
        else:
            fc, ec = {"normal": (BLUE_F, BLUE_E), "x": (RED_F, RED_E),
                      "pg": (GRN_F, GRN_E)}[n.style]
            rr = R + 0.105 * max(0, len(n.label) - 1)
            ax.add_patch(Circle((n.x, n.y), rr, fc=fc, ec=ec, lw=1.7, zorder=2))
        ax.text(n.x, n.y, n.label, ha="center", va="center",
                fontsize=(11 if len(n.label) < 2 else 9.5),
                color="#111827", zorder=3)
        if n.note is not None:                     # depth / extra annotation
            ax.text(n.x + BW / 2 + 0.10 if n.box else n.x + R + 0.10, n.y, n.note,
                    ha="left", va="center", fontsize=8.5, color="#1d4ed8", zorder=3)
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
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        os.path.basename(path))
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print("wrote", path, flush=True)


def box(l, key=None):
    return N(l, box=True, note=key)


def node(l, left=None, right=None, style="normal", note=None):
    return N(l, left, right, style=style, note=note)


X = lambda l, a=None, b=None: node(l, a, b, style="x")
PG = lambda l, a=None, b=None: node(l, a, b, style="pg")


# ---------------------------------------------------------------------------
# the three splay cases, drawn by hand (labels X / P / G, subtrees A..D)
# ---------------------------------------------------------------------------
def fig_zig():
    before = PG("P", X("X", box("$A$"), box("$B$")), box("$C$"))
    after = X("X", box("$A$"), PG("P", box("$B$"), box("$C$")))
    save([{"root": before, "title": "Zig (before): parent of $X$ is the root",
           "caption": "single rotation at $P$"},
          {"root": after, "title": "Zig (after)",
           "caption": "$X$ is the new root; $A$ stays, $B$ moves to $P$"}],
         "fig_splay_zig.png", width=8.6)


def fig_zigzig():
    p1 = PG("G", PG("P", X("X", box("$A$"), box("$B$")), box("$C$")), box("$D$"))
    p2 = PG("P", X("X", box("$A$"), box("$B$")), PG("G", box("$C$"), box("$D$")))
    p3 = X("X", box("$A$"), PG("P", box("$B$"), PG("G", box("$C$"), box("$D$"))))
    save([{"root": p1, "title": "Zig-zig (before): $X$, $P$ both left children",
           "caption": "2 single rotations, bottom-up"},
          {"root": p2, "title": "Step 1: rotate $P$ and $G$",
           "caption": "single rotation at $G$; $X$ unchanged"},
          {"root": p3, "title": "Step 2: rotate $X$ and $P$",
           "caption": "$X$ is the root, $P$ its right child, $G$ below $P$"}],
         "fig_splay_zigzig.png", width=11.6)


def fig_zigzag():
    p1 = PG("G", PG("P", box("$A$"), X("X", box("$B$"), box("$C$"))), box("$D$"))
    p2 = PG("G", X("X", PG("P", box("$A$"), box("$B$")), box("$C$")), box("$D$"))
    p3 = X("X", PG("P", box("$A$"), box("$B$")), PG("G", box("$C$"), box("$D$")))
    save([{"root": p1, "title": "Zig-zag (before): $X$ and $P$ on opposite sides",
           "caption": "$X$ is a right child, $P$ a left child"},
          {"root": p2, "title": "Step 1: rotate $X$ and $P$",
           "caption": "single rotation at $P$"},
          {"root": p3, "title": "Step 2: rotate $X$ and $G$",
           "caption": "identical to an AVL double rotation"}],
         "fig_splay_zigzag.png", width=11.6)


# ---------------------------------------------------------------------------
# rotate-to-root vs. splay on a skew tree (simulated, not hand-drawn)
# ---------------------------------------------------------------------------
class T:
    def __init__(self, k):
        self.k, self.l, self.r = k, None, None


def rot_right(x):                     # x.l goes up
    y = x.l
    x.l = y.r
    y.r = x
    return y


def rot_left(x):                      # x.r goes up
    y = x.r
    x.r = y.l
    y.l = x
    return y


def move_to_root(x, k):               # rotate-to-root: one rotation at a time
    if x is None or x.k == k:
        return x
    if k < x.k:
        x.l = move_to_root(x.l, k)
        if x.l is not None and x.l.k == k:
            x = rot_right(x)
    else:
        x.r = move_to_root(x.r, k)
        if x.r is not None and x.r.k == k:
            x = rot_left(x)
    return x


def splay(x, k):                      # bottom-up splay: rotations in pairs
    if x is None or x.k == k:
        return x
    if k < x.k:
        p = x.l
        if p is None:
            return x
        if k == p.k:                                  # zig
            return rot_right(x)
        if k < p.k:                                   # zig-zig
            x.l.l = splay(x.l.l, k)
            x = rot_right(x)                          # rotate P and G
            return rot_right(x)                       # rotate X and P
        x.l.r = splay(x.l.r, k)                       # zig-zag
        x.l = rot_left(x.l)
        return rot_right(x)
    p = x.r
    if p is None:
        return x
    if k == p.k:                                      # zig (mirror)
        return rot_left(x)
    if k > p.k:                                       # zig-zig (mirror)
        x.r.r = splay(x.r.r, k)
        x = rot_left(x)
        return rot_left(x)
    x.r.l = splay(x.r.l, k)                           # zig-zag (mirror)
    x.r = rot_right(x.r)
    return rot_left(x)


def to_N(t, depths=None):
    """Turn a simulated tree into the drawing structure, remembering depths."""
    if depths is None:
        depths = {}

    def build(n, depth):
        depths[n.k] = depth
        return N(str(n.k),
                 None if n.l is None else build(n.l, depth + 1),
                 None if n.r is None else build(n.r, depth + 1))

    return build(t, 0), depths


def chain(vals):
    t = None
    for v in vals:                      # vals = 7,6,...,1  ->  all-left chain
        t = T(v) if t is None else _attach(t, v)
    return t


def _attach(t, v):
    if v < t.k:
        t.l = T(v) if t.l is None else _attach(t.l, v)
    else:
        t.r = T(v) if t.r is None else _attach(t.r, v)
    return t


def fig_vs_single():
    start = chain(range(7, 0, -1))      # 7 <- 6 <- ... <- 1, all left children
    single = move_to_root(chain(range(7, 0, -1)), 1)
    splayed = splay(chain(range(7, 0, -1)), 1)
    n_start, d0 = to_N(start)
    n_single, d1 = to_N(single)
    n_splay, d2 = to_N(splayed)

    def deepest(d):
        k = max(d, key=lambda i: d[i])
        return k, d[k]

    k1, v1 = deepest(d1)
    k2, v2 = deepest(d2)
    save([{"root": n_start, "title": "Skew tree: all left children",
           "caption": "root 7; node 1 is at depth 6"},
          {"root": n_single, "title": "After single rotations (rotate-to-root)",
           "caption": "node %d is still at depth %d\n"
                      "the chain is only flipped over" % (k1, v1)},
          {"root": n_splay, "title": "After splay(1)",
           "caption": "deepest node now at depth %d\n"
                      "most depths are roughly halved" % v2}],
         "fig_splay_vs_single.png", width=13.0)


if __name__ == "__main__":
    fig_zig()
    fig_zigzig()
    fig_zigzag()
    fig_vs_single()

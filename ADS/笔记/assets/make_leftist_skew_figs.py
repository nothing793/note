#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the figures for ADS/笔记/05_ADS04_左式堆与斜堆.md.

Everything here is redrawn from the lecture deck
`Materials/Student Slides/ADS04LeftistSkewH_Stu.ppt`: H1 / H2, the merge results
and the heavy-light example were read off the shapes of that deck, and the
merge results are re-derived by simulating the algorithms of the note itself
(`merge_leftist`, `merge_skew`, insert = merge with a one-node heap).  The tree
layouts are our own drawing.

Node labels are Latin/mathtext only: the CJK font on this machine carries no
Latin glyphs, so mixed-language labels would come out as boxes.

Run:  python3 make_leftist_skew_figs.py     (writes fig_*.png next to this file)
"""
import copy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["axes.unicode_minus"] = False

FACE = {"plain": ("#e5e7eb", "#374151"),       # ordinary node
        "path": ("#bfdbfe", "#1d4ed8"),        # node on a right path (light node)
        "swapped": ("#fecaca", "#b91c1c"),     # node whose children were swapped
        "heavy": ("#fed7aa", "#c2410c"),       # heavy node
        "new": ("#bbf7d0", "#15803d")}         # freshly inserted node
EDGE, PATH_EDGE = "#94a3b8", "#2563eb"
R, DY = 0.35, 1.0


class Node:
    def __init__(self, label, left=None, right=None, kind="plain", npl=None,
                 note=None):
        self.label = str(label)
        self.left, self.right = left, right
        self.kind, self.npl, self.note = kind, npl, note

    def key(self):
        return int(self.label)


# ------------------------------------------------------------ tree utilities
def size(n):
    return 0 if n is None else 1 + size(n.left) + size(n.right)


def npl(n):
    """npl from the definition (the npl attribute is only used for display)."""
    if n is None:
        return -1
    return 1 + min(npl(n.left), npl(n.right))


def fill_npl(n):
    if n is None:
        return -1
    n.npl = 1 + min(fill_npl(n.left), fill_npl(n.right))
    return n.npl


def canonical(n):
    if n is None:
        return ""
    parts = [p for p in (canonical(n.left), canonical(n.right)) if p]
    return n.label if not parts else "%s(%s)" % (n.label, ",".join(parts))


def right_path(n):
    out = []
    while n is not None:
        out.append(n)
        n = n.right
    return out


def walk(n, depth=0, f=None):
    if n is None:
        return
    f(n, depth)
    walk(n.left, depth + 1, f)
    walk(n.right, depth + 1, f)


def mark(root, kinds):
    """kinds: {label: kind}; the first matching node in pre-order wins."""
    taken = set()

    def f(n, d):
        if n.label in kinds and n.label not in taken:
            n.kind = kinds[n.label]
            taken.add(n.label)

    walk(root, f=f)


# ------------------------------------------------------- the algorithms itself
def merge_leftist(h1, h2):
    """Weiss' recursive leftist merge (note section 2.3)."""
    if h1 is None:
        return h2
    if h2 is None:
        return h1
    if h1.key() > h2.key():
        h1, h2 = h2, h1
    old_left = h1.left
    if old_left is None:                      # single node: H1->Right is NULL too
        h1.left, h1.npl = h2, 0
        return h1
    h1.right = merge_leftist(h1.right, h2)
    if npl(old_left) < npl(h1.right):
        h1.left, h1.right = h1.right, h1.left
    h1.npl = npl(h1.right) + 1
    return h1


def merge_skew(h1, h2):
    """Skew merge: always swap on the way back (note section 3.2)."""
    if h1 is None:
        return h2
    if h2 is None:
        return h1
    if h1.key() > h2.key():
        h1, h2 = h2, h1
    h1.right = merge_skew(h1.right, h2)
    h1.left, h1.right = h1.right, h1.left
    return h1


def sort_right_paths(h1, h2):
    """Iterative step 1: sort both right paths into one, keep the left children."""
    chain = sorted([(n.key(), n.left) for n in right_path(h1)] +
                   [(n.key(), n.left) for n in right_path(h2)])
    root = Node(chain[0][0], chain[0][1])
    cur = root
    for key, left in chain[1:]:
        cur.right = Node(key, left)
        cur = cur.right
    return root


def fill_leftist(root):
    """Bottom-up swap while npl(left) < npl(right), the iterative step 2."""
    for n in reversed(right_path(root)):
        if npl(n.left) < npl(n.right):
            n.left, n.right = n.right, n.left
    return root


# ------------------------------------------------------------- example trees
def h1():
    """H1 (root 3) of the lecture example: 3(10(21,14(23)), 8(17(26)))."""
    return Node(3, Node(10, Node(21), Node(14, Node(23))),
                Node(8, Node(17, Node(26))))


def h2():
    """H2 (root 6): 6(12(18,24(33)), 7(37,18))."""
    return Node(6, Node(12, Node(18), Node(24, Node(33))),
                Node(7, Node(37), Node(18)))


def heavy_light_pair():
    """The two heaps of the 'Amortized Analysis for Skew Heaps' slide."""
    t1 = Node(3, Node(6, Node(10), Node(14, Node(16))),
              Node(8, Node(9, None, Node(12)), Node(17)))
    t2 = Node(1, Node(2), Node(5, Node(11), Node(7)))
    return t1, t2


# ------------------------------------------------------------------ rendering
def layout(root, dx=1.0, offset=0.0):
    slot = [0]

    def inorder(n):
        if n is None:
            return
        inorder(n.left)
        n.x = slot[0] * dx
        slot[0] += 1
        inorder(n.right)

    def depths(n, depth):
        n.y = -depth * DY

    inorder(root)
    walk(root, f=depths)
    walk(root, f=lambda n, d: setattr(n, "x", n.x + offset))


def draw_tree(ax, root, dx=1.0, offset=0.0, path=(), show_npl=False,
              radius=R, fontsize=10.5):
    layout(root, dx, offset)
    path = list(path)
    xs, ys = [], []

    def on_path(p, c):
        return any(path[i] is p and path[i + 1] is c
                   for i in range(len(path) - 1))

    def edges(n):
        for c in (n.left, n.right):
            if c is None:
                continue
            if on_path(n, c):
                ax.plot([n.x, c.x], [n.y, c.y], color=PATH_EDGE, lw=2.6, zorder=1)
            else:
                ax.plot([n.x, c.x], [n.y, c.y], color=EDGE, lw=1.2, zorder=1)
            edges(c)

    def circles(n):
        face, edge = FACE[n.kind]
        ax.add_patch(plt.Circle((n.x, n.y), radius, fc=face, ec=edge, lw=1.7,
                                zorder=2))
        ax.text(n.x, n.y, n.label, ha="center", va="center", fontsize=fontsize,
                color="#111827", zorder=3)
        if show_npl and n.npl is not None:
            ax.text(n.x + radius + 0.06, n.y + 0.12, "npl=%d" % n.npl, ha="left",
                    va="bottom", fontsize=8, color="#1d4ed8", zorder=3)
        if n.note:
            ax.text(n.x, n.y + radius + 0.08, n.note, ha="center", va="bottom",
                    fontsize=8, color="#b91c1c", zorder=3)
        xs.append(n.x)
        ys.append(n.y)
        for c in (n.left, n.right):
            if c is not None:
                circles(c)

    edges(root)
    circles(root)
    return xs, ys


def finish(ax, extents, title=None, pad=0.7):
    xs = [x for e in extents for x in e[0]]
    ys = [y for e in extents for y in e[1]]
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad + 0.6)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=10, color="#111827", pad=8)


def save(fig, name, title):
    fig.suptitle(title, fontsize=11.5, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    fig.savefig(name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------- figures
def fig_heaps(name):
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 3.6))
    for ax, root, tag in ((axes[0], h1(), "H1"), (axes[1], h2(), "H2")):
        fill_npl(root)
        p = right_path(root)
        e = draw_tree(ax, root, dx=1.7, path=p, show_npl=True)
        finish(ax, [e], title="%s: %d nodes, right path %s (%d nodes)" %
               (tag, size(root), " -> ".join(n.label for n in p), len(p)))
    save(fig, name, "The two leftist heaps of the lecture example: npl(left) >= "
                    "npl(right) at every node; blue = npl, thick blue = right path")


def fig_merge_steps(name):
    a, b = h1(), h2()
    step1 = merge_leftist(copy.deepcopy(a.right), copy.deepcopy(b))
    merged = merge_leftist(copy.deepcopy(a), copy.deepcopy(b))
    assert canonical(merged) == "3(6(12(18,24(33)),7(8(17(26),18),37)),10(21,14(23)))", \
        canonical(merged)
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.8))
    e1 = draw_tree(axes[0][0], a, path=right_path(a))
    finish(axes[0][0], [e1], title="(1) H1: right path 3 -> 8")
    e2 = draw_tree(axes[0][1], b, path=right_path(b))
    finish(axes[0][1], [e2], title="(1) H2: right path 6 -> 7 -> 18")
    e3 = draw_tree(axes[1][0], step1, path=right_path(step1))
    finish(axes[1][0], [e3],
           title="(3) Step 1: Merge(H1->Right, H2) -- 6 becomes the new root")
    merged_marks = copy.deepcopy(merged)
    mark(merged_marks, {"7": "swapped", "3": "swapped"})
    e4 = draw_tree(axes[1][1], merged_marks)
    finish(axes[1][1], [e4],
           title="(4) Step 2 attach as H1->Right, Step 3 swap at 3 "
                 "(red = 3 and 7: the only nodes whose children were swapped)")
    save(fig, name, "Leftist merge, recursive version: only the two right paths "
                    "are walked, T_p = O(log N)")


def fig_merge_iterative(name):
    a, b = h1(), h2()
    step1 = sort_right_paths(copy.deepcopy(a), copy.deepcopy(b))
    final = fill_leftist(copy.deepcopy(step1))
    assert canonical(final) == "3(6(12(18,24(33)),7(8(17(26),18),37)),10(21,14(23)))", \
        canonical(final)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.4))
    e1 = draw_tree(axes[0], a, path=right_path(a))
    e2 = draw_tree(axes[0], b, offset=size(a) + 1.2, path=right_path(b))
    finish(axes[0], [e1, e2],
           title="(1) H1 and H2: right paths 3->8 and 6->7->18")
    e3 = draw_tree(axes[1], step1, path=right_path(step1))
    finish(axes[1], [e3],
           title="(2) Step 1: sorted right path 3->6->7->8->18, "
                 "left children untouched")
    e4 = draw_tree(axes[2], final)
    finish(axes[2], [e4],
           title="(3) Step 2: swap bottom-up where npl(left) < npl(right)")
    save(fig, name, "Leftist merge, iterative version: same result as the "
                    "recursive version, T_p = O(log N)")


def fig_skew_merge(name):
    a, b = h1(), h2()
    left = merge_leftist(copy.deepcopy(a), copy.deepcopy(b))
    skew = merge_skew(copy.deepcopy(a), copy.deepcopy(b))
    assert canonical(skew) == "3(6(7(8(18,17(26)),37),12(18,24(33))),10(21,14(23)))", \
        canonical(skew)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))
    e1 = draw_tree(axes[0], a, path=right_path(a))
    e2 = draw_tree(axes[0], b, offset=size(a) + 1.2, path=right_path(b))
    finish(axes[0], [e1, e2],
           title="(1) the same H1 and H2, right paths 3->8 and 6->7->18")
    skew_marks = copy.deepcopy(skew)
    mark(skew_marks, {"3": "swapped", "6": "swapped", "7": "swapped",
                      "8": "swapped"})
    e3 = draw_tree(axes[1], skew_marks)
    finish(axes[1], [e3],
           title="(2) skew merge: 3, 6, 7, 8 swap their children on the way back "
                 "(red)")
    e4 = draw_tree(axes[2], left)
    finish(axes[2], [e4],
           title="(3) leftist merge of the very same pair: those nodes keep "
                 "their children")
    save(fig, name, "Skew heap merge: always swap, no npl; amortized T = O(log N) "
                    "(a single merge can be linear)")


def fig_insert15(name):
    base = merge_skew(copy.deepcopy(h1()), copy.deepcopy(h2()))
    after = merge_skew(copy.deepcopy(base), Node(15))
    assert canonical(after) == \
        "3(10(14(15,23),21),6(7(8(18,17(26)),37),12(18,24(33))))", canonical(after)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    e1 = draw_tree(axes[0], base, path=right_path(base))
    finish(axes[0], [e1],
           title="(1) before: 15 is merged with the skew heap of the previous "
                 "example (right path 3 -> 10 -> 14)")
    after_marks = copy.deepcopy(after)
    mark(after_marks, {"15": "new", "14": "swapped", "10": "swapped",
                       "3": "swapped"})
    e2 = draw_tree(axes[1], after_marks)
    finish(axes[1], [e2],
           title="(2) after: 15 becomes 14->left, then 14, 10, 3 swap their "
                 "children on the way back")
    save(fig, name, "Skew heap Insert 15 = merge with a one-node heap: insertion "
                    "is nothing but merge")


def heavy_marks(root):
    """Colour nodes by the note's heavy/light definition; return the counts."""
    p = right_path(root)
    light_path = heavy_path = heavy_rest = 0

    def f(n, d):
        nonlocal light_path, heavy_path, heavy_rest
        heavy = 2 * size(n.right) >= size(n)
        n.kind = "heavy" if heavy else ("path" if n in p else "plain")
        n.note = "heavy" if (heavy and n not in p) else None
        if n in p:
            if heavy:
                heavy_path += 1
            else:
                light_path += 1
        elif heavy:
            heavy_rest += 1

    walk(root, f=f)
    return light_path, heavy_path, heavy_rest


def fig_potential(name):
    t1, t2 = heavy_light_pair()
    t1b, t2b = copy.deepcopy(t1), copy.deepcopy(t2)
    l1, hp1, hr1 = heavy_marks(t1b)
    l2, hp2, hr2 = heavy_marks(t2b)
    after = merge_skew(copy.deepcopy(t1), copy.deepcopy(t2))
    after_b = copy.deepcopy(after)
    l3, hp3, hr3 = heavy_marks(after_b)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))
    e1 = draw_tree(axes[0], t1b, path=right_path(t1b))
    finish(axes[0], [e1],
           title="H1 (root 3): right path 3->8->17, l1 = %d light, h1 = %d heavy"
                 % (l1, hp1))
    e2 = draw_tree(axes[1], t2b, path=right_path(t2b))
    finish(axes[1], [e2],
           title="H2 (root 1): right path 1->5->7, l2 = %d light, h2 = %d heavy"
                 % (l2, hp2))
    e3 = draw_tree(axes[2], after_b)
    finish(axes[2], [e3],
           title="after the merge: heavy nodes = %d, right path 1->2"
                 % (hp3 + hr3))
    save(fig, name, "Heavy nodes (orange) and the potential function of this "
                    "example: Phi_i = h1 + h2 + h = %d + %d + %d = %d, "
                    "T_amortized <= 2(l1 + l2)"
                    % (hp1, hp2, hr1 + hr2, hp1 + hp2 + hr1 + hr2))


def main():
    fig_heaps("fig_leftist_heaps_h1h2.png")
    fig_merge_steps("fig_leftist_merge_steps.png")
    fig_merge_iterative("fig_leftist_merge_iterative.png")
    fig_skew_merge("fig_skew_merge.png")
    fig_insert15("fig_skew_insert15.png")
    fig_potential("fig_skew_potential.png")


if __name__ == "__main__":
    main()

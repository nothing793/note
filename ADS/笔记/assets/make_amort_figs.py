#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the amortized-analysis figures used in ADS/笔记/02_ADS001_伸展树与摊还分析.md.

Two figures:

  fig_amort_sizes.png   -- the size bookkeeping behind the zig-zag and zig-zig
                           bounds (which subtree sizes are added, and why the
                           sum is at most S_2(X)).
  fig_amort_ledger.png  -- a real simulation of a splay tree: actual cost per
                           operation vs. amortized cost, and the cumulative
                           ledger.  The same run also checks, numerically,
                           the per-step bounds used in the proof.

Conventions follow make_splay_figs.py: figures carry Latin/mathtext labels only
(the CJK explanation lives in the markdown); trees in fig_amort_sizes.png are
hand-built, the ledger figure is computed by actually running the algorithms.

Run:  python3 make_amort_figs.py
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.dont_write_bytecode = True          # keep the folder free of __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_splay_figs import N, box, node, save, X, PG, BLUE_E, PG as _PG  # noqa

plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------------------
# 1. size bookkeeping for the zig-zag and zig-zig bounds
# ---------------------------------------------------------------------------
def fig_sizes():
    zz_before = PG("G", PG("P", box("$A$"), X("X", box("$B$"), box("$C$"))),
                   box("$D$"))
    zz_after = X("X", PG("P", box("$A$"), box("$B$")),
                 PG("G", box("$C$"), box("$D$")))
    zz_cap = ("after the step:  $S_2(P)=|A|+|B|+1$,  $S_2(G)=|C|+|D|+1$,\n"
              "$S_2(P)+S_2(G)=S_2(X)-1\\ \\leq\\ S_2(X)$  $\\Rightarrow$  "
              "$R_2(P)+R_2(G)\\leq 2R_2(X)-2$")

    zi_before = PG("G", PG("P", X("X", box("$A$"), box("$B$")), box("$C$")),
                   box("$D$"))
    zi_after = X("X", box("$A$"),
                 PG("P", box("$B$"), PG("G", box("$C$"), box("$D$"))))
    zi_cap = ("after the step:  $S_1(X)=|A|+|B|+1$,  $S_2(G)=|C|+|D|+1$,\n"
              "$S_1(X)+S_2(G)=S_2(X)-1\\ \\leq\\ S_2(X)$  $\\Rightarrow$  "
              "$R_1(X)+R_2(G)\\leq 2R_2(X)-2$")

    save([{"root": zz_before, "title": "Zig-zag, step $i$ (before)",
           "caption": "$X$, $P$ on opposite sides"},
          {"root": zz_after, "title": "Zig-zag (after)",
           "caption": zz_cap},
          {"root": zi_before, "title": "Zig-zig, step $i$ (before)",
           "caption": "$X$, $P$ both left children"},
          {"root": zi_after, "title": "Zig-zig (after)",
           "caption": zi_cap}],
         "fig_amort_sizes.png", width=10.6, ncols=2, extra_h=1.15)


# ---------------------------------------------------------------------------
# 2. ledger figure: simulate a splay tree, plot actual vs. amortized cost
# ---------------------------------------------------------------------------
class SN:
    __slots__ = ("k", "l", "r")

    def __init__(self, k):
        self.k, self.l, self.r = k, None, None


def size(t):
    return 0 if t is None else 1 + size(t.l) + size(t.r)


def phi(t):
    return 0.0 if t is None else math.log2(size(t)) + phi(t.l) + phi(t.r)


def rank(t, k):
    """log2 of the size of the subtree rooted at the node with key k."""
    while t is not None and t.k != k:
        t = t.l if k < t.k else t.r
    return math.log2(size(t)) if t is not None else float("nan")


def rot_right(x):
    y = x.l
    x.l = y.r
    y.r = x
    return y


def rot_left(x):
    y = x.r
    x.r = y.l
    y.l = x
    return y


def splay_step(root, key, steps):
    """One pair of rotations (bottom-up); appends (kind, rot_count) to steps."""
    if root is None or root.k == key:
        return root
    if key < root.k:
        p = root.l
        if p is None:
            return root
        if key == p.k:                                  # zig
            steps.append(("zig", 1))
            return rot_right(root)
        if key < p.k:                                   # zig-zig
            steps.append(("zig-zig", 2))
            root.l.l = splay_step(root.l.l, key, steps)
            root = rot_right(root)                      # rotate P and G
            return rot_right(root)                      # rotate X and P
        steps.append(("zig-zag", 2))                    # zig-zag
        root.l.r = splay_step(root.l.r, key, steps)
        root.l = rot_left(root.l)
        return rot_right(root)
    p = root.r
    if p is None:
        return root
    if key == p.k:
        steps.append(("zig", 1))
        return rot_left(root)
    if key > p.k:
        steps.append(("zig-zig", 2))
        root.r.r = splay_step(root.r.r, key, steps)
        root = rot_left(root)
        return rot_left(root)
    steps.append(("zig-zag", 2))
    root.r.l = splay_step(root.r.l, key, steps)
    root.r = rot_right(root.r)
    return rot_left(root)


def splay_verified(root, key, check):
    """Bottom-up splay; checks every step against its amortized bound."""
    steps = []
    while root is not None and root.k != key:
        before = rank(root, key)
        root = splay_step(root, key, steps)
        after = rank(root, key)
        kind, nrot = steps[-1]
        bound = 3 * (after - before) + (1 if kind == "zig" else 0)
        check.append((kind, nrot, before, after, bound))
    return root


def insert(root, key):
    if root is None:
        return SN(key)
    t = root
    while True:
        if key < t.k:
            if t.l is None:
                t.l = SN(key)
                break
            t = t.l
        else:
            if t.r is None:
                t.r = SN(key)
                break
            t = t.r
    return root


def run(n=63, m=None):
    """Build 1..n by inserting and splaying, then use a nasty access pattern."""
    keys = list(range(1, n + 1))
    accesses = []
    lo, hi = 0, n - 1
    while lo <= hi:                                     # 1, n, 2, n-1, 3, ...
        accesses.append(keys[lo])
        if hi != lo:
            accesses.append(keys[hi])
        lo, hi = lo + 1, hi - 1
    if m:
        accesses = accesses[:m]

    root, check, log = None, [], []
    pot = 0.0
    for k in keys:
        root = insert(root, k)
        nrot = 0
        steps = []
        while root.k != k:
            before = rank(root, k)
            root = splay_step(root, k, steps)
            nrot += 1
            kind, cnt = steps[-1]
            check.append((kind, cnt, before, rank(root, k),
                          3 * (rank(root, k) - before) + (1 if kind == "zig" else 0)))
        c = 1 + sum(cnt for _, cnt in steps)            # textbook cost model
        new_pot = phi(root)
        log.append(("insert", k, c, c + new_pot - pot, new_pot))
        pot = new_pot
    mark = len(log)
    for k in accesses:
        steps = []
        while root.k != k:
            before = rank(root, k)
            root = splay_step(root, k, steps)
            kind, cnt = steps[-1]
            check.append((kind, cnt, before, rank(root, k),
                          3 * (rank(root, k) - before) + (1 if kind == "zig" else 0)))
        c = 1 + sum(cnt for _, cnt in steps)
        new_pot = phi(root)
        log.append(("find", k, c, c + new_pot - pot, new_pot))
        pot = new_pot
    return log, check, mark, n


def fig_ledger():
    log, check, mark, n = run(63)
    c = [r[2] for r in log]
    chat = [r[3] for r in log]
    pot = [r[4] for r in log]
    M = len(log)
    bound = 3 * math.log2(n) + 1
    cum_c, cum_chat = [], []
    sc = sc_hat = 0.0
    for i in range(M):
        sc += c[i]
        sc_hat += chat[i]
        cum_c.append(sc)
        cum_chat.append(sc_hat)

    # --- numeric self-check of the proof ---
    bad_step = [x for x in check if x[1] > x[4] + 1e-9]
    bad_op = [i for i in range(M) if chat[i] > bound + 1e-9]
    print("steps checked                :", len(check))
    print("step bound violated          :", len(bad_step))
    print("max per-step slack           :",
          max(x[4] - x[1] for x in check))
    print("Sum chat >= Sum c            :", sc_hat >= sc - 1e-9,
          "(diff = %.2f)" % (sc_hat - sc))
    print("max per-op amortized cost    : %.3f  (3 log2 n + 1 = %.3f, "
          "violations: %d)" % (max(chat), bound, len(bad_op)))
    print("total actual cost            : %.0f  (bound M*(3log2 n+1) = %.0f)"
          % (sc, M * bound))
    print("build/access split           :", mark, "/", M - mark)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 4.6))
    idx = range(1, M + 1)

    ax1.axvline(mark + 0.5, color="#94a3b8", ls="--", lw=1.1)
    ax1.bar(idx, c, color="#bfdbfe", ec="#1d4ed8", lw=0.7, width=0.85,
            label="actual cost $c_i$")
    ax1.plot(idx, chat, "o-", color="#b91c1c", ms=3.2, lw=1.1,
             label="amortized cost $\\hat{c}_i$")
    ax1.axhline(bound, color="#15803d", ls=":", lw=1.6,
                label="$3\\log_2 n + 1 = %.1f$" % bound)
    ax1.set_xlabel("operation ($1\\ldots 63$: inserts; then finds)")
    ax1.set_ylabel("cost")
    ax1.set_title("Per-operation cost, $n=63$", fontsize=11.5)
    ax1.legend(fontsize=8.5, loc="lower left")
    ax1.grid(alpha=0.25)
    ax1.axhline(0.0, color="#94a3b8", lw=1.0)
    k = max(range(M), key=lambda i: c[i])
    ax1.annotate("worst single operation: %.0f rotations, $c=%.0f$\n"
                 "$\\hat{c}=c+\\Delta\\Phi=%.0f$ : paid with the potential "
                 "saved\nby the cheap operations before it"
                 % (c[k] - 1, c[k], chat[k]),
                 xy=(k + 1, c[k]), xytext=(k + 4, 80), va="top",
                 fontsize=8.5, color="#111827",
                 arrowprops=dict(arrowstyle="->", color="#64748b", lw=1.1))
    ax1.set_ylim(-125, 85)

    ax2.axvline(mark + 0.5, color="#94a3b8", ls="--", lw=1.1,
                label="end of build phase")
    ax2.plot(idx, cum_c, color="#1d4ed8", lw=1.6,
             label="cumulative actual $\\sum c_i$")
    ax2.plot(idx, cum_chat, color="#b91c1c", lw=1.6,
             label="cumulative amortized $\\sum \\hat{c}_i = \\sum c_i + \\Phi$")
    ax2.plot(idx, [i * bound for i in idx], color="#15803d", ls=":",
             lw=1.6, label="bound $M(3\\log_2 n+1)$")
    ax2.set_xlabel("operation")
    ax2.set_ylabel("cumulative cost")
    ax2.set_title("The ledger: $\\sum\\hat{c}_i \\geq \\sum c_i$, "
                  "$\\sum\\hat{c}_i = O(M\\log n)$", fontsize=11.5)
    ax2.legend(fontsize=8.5, loc="upper left")
    ax2.grid(alpha=0.25)

    ax2.set_yscale("log")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "fig_amort_ledger.png")
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    fig_sizes()
    fig_ledger()

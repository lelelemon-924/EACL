#!/usr/bin/env python3
"""Regenerate every figure asset from the reported results.

All numbers are transcribed from ``final_result.md``. Running this script writes,
into ``../figures``:

    fig1a_concept.pdf      PLACEHOLDER  -> author by hand, see FIGURE_GUIDE.md
    fig1b_reversal.pdf     preference-reversal bars                    [E0/E1]
    fig2_pipeline.pdf      PLACEHOLDER  -> author by hand, see FIGURE_GUIDE.md
    fig3_diagnostics.pdf   AUROC forest + attack success by margin bin [E6]
    fig4_depth.pdf         attack success vs reached-state depth        [E4]

Usage:
    python scripts/make_figures.py

Dependencies: numpy, matplotlib.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "figures"))
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared design system. One palette, one type scale, used by every panel so the
# figures read as a set rather than as five unrelated plots.
# ---------------------------------------------------------------------------
INK = "#1A1A1A"          # primary text
MUTED = "#6E7681"        # secondary text
GRID = "#DFE3E8"         # gridlines
OURS = "#1F6F54"         # CURE-DPO
OURS_LT = "#8FBFAC"      # CURE-DPO, light fill
EXT = "#B4607F"          # non-method accent: fitted curves only
COOL = "#4A7DB5"         # non-method accent: reached-state blue

# Method series share one grey ramp instead of one hue each. Only three rows
# carry the argument -- Base sets the reference, W-DOOR is the strongest
# external defense, CURE-DPO is ours -- so spending a separate colour on the
# remaining baselines makes the reader decode a legend to learn nothing. Rank
# in the ramp encodes how much attention a series is owed, and the series stay
# distinguishable in grayscale.
BASE = "#98A2B3"         # untrained base, the reference row
STRONG_EXT = "#5F6874"   # W-DOOR, strongest external defense
NEUTRAL = "#AAB3BF"      # remaining baselines
NEUTRAL_LT = "#C6CED8"   # kept dark enough to survive a 100% print

plt.rcParams.update(
    {
        "font.size": 8,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": MUTED,
        "axes.labelsize": 8,
        "axes.titlesize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 7.2,
        "ytick.labelsize": 7.2,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "legend.fontsize": 7.0,
        "legend.frameon": False,
        "legend.handlelength": 1.6,
        "legend.labelspacing": 0.3,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "savefig.pad_inches": 0.015,
        "pdf.fonttype": 42,
    }
)

# The widths paper.tex places each figure at. \textwidth is 455.24 pt and
# \columnsep is 0.6 cm, so a column is (455.24 - 17.01) / 2 pt.
TEXT_WIDTH_IN = 6.323
COLUMN_WIDTH_IN = 3.043


def save_exact(fig, path, width_in, height_in, **layout):
    """Write the figure at exactly the size it is placed at on the page.

    ``savefig(bbox_inches="tight")`` crops to the drawn content, so the file is
    not the requested ``figsize``; LaTeX then scales it to the
    ``\\includegraphics`` width and every font size inside moves with that
    factor. fig1b was being shrunk 13% this way, which put its tick labels at
    6.1 pt. Fixing the canvas and letting ``tight_layout`` pack the axes inside
    it keeps a requested point size a printed point size.
    """
    fig.set_size_inches(width_in, height_in)
    fig.tight_layout(pad=0.3, **layout)
    fig.savefig(path, bbox_inches=None)
    plt.close(fig)
    return path


def _placeholder(path, width_in, height_in, title, lines):
    """A clearly-marked placeholder box at the exact size of the final figure.

    Compiling with these in place produces a PDF whose layout already matches
    the camera-ready one, so the hand-authored figure can be dropped in without
    reflowing the paper. Once the figure has been authored in draw.io, the
    exported PDF must survive a rerun of this script, so a sibling ``.drawio``
    source suppresses the placeholder.
    """
    if os.path.exists(os.path.splitext(path)[0] + ".drawio"):
        return path + "  (kept: authored in draw.io)"

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.set_axis_off()
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0.008, 0.012),
            0.984,
            0.976,
            boxstyle="round,pad=0.004,rounding_size=0.012",
            transform=ax.transAxes,
            facecolor="#F7F8FA",
            edgecolor=EXT,
            linewidth=1.0,
            linestyle=(0, (5, 3)),
        )
    )
    ax.text(
        0.5, 0.80, title, transform=ax.transAxes, ha="center", va="center",
        fontsize=10, fontweight="bold", color=EXT,
    )
    ax.text(
        0.5, 0.50, "\n".join(lines), transform=ax.transAxes, ha="center",
        va="center", fontsize=7.4, color=MUTED, linespacing=1.6,
    )
    ax.text(
        0.5, 0.14, "authoring instructions: figures/FIGURE_GUIDE.md",
        transform=ax.transAxes, ha="center", va="center", fontsize=6.8,
        color=EXT, style="italic",
    )
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Figure 1(a): the same-state concept. Hand-authored (draw.io / Illustrator).
# ---------------------------------------------------------------------------
def make_fig1a():
    return _placeholder(
        os.path.join(OUT, "fig1a_concept.pdf"),
        3.72, 2.62,
        "Figure 1(a)  —  placeholder",
        [
            "Same-state control: one reached unsafe state,",
            "two alternative futures, opposite preferences.",
            "",
            "target size 3.72 in x 2.62 in (0.54 textwidth)",
        ],
    )


# ---------------------------------------------------------------------------
# Figure 2: the four-stage pipeline. Hand-authored, full text width.
# ---------------------------------------------------------------------------
def make_fig2():
    return _placeholder(
        os.path.join(OUT, "fig2_pipeline.pdf"),
        6.90, 1.95,
        "Figure 2  —  placeholder",
        [
            "CURE-DPO pipeline: reached states -> matched same-state pair",
            "-> same-state preference loss -> lower-tail selection + anchors.",
            "",
            "target size 6.90 in x 1.95 in (full textwidth banner)",
        ],
    )


# ---------------------------------------------------------------------------
# Figure 1(b): preference-reversal fractions. W-DOOR included so the headline
# figure compares against the strongest external baseline, not only internally.
# ---------------------------------------------------------------------------
REVERSAL = [
    ("Base", 47.9, 0.8, BASE),
    ("Clean DPO", 41.3, 1.1, NEUTRAL),
    ("Recovery SFT", 32.4, 1.0, NEUTRAL),
    ("Uniform same-state", 23.2, 1.2, NEUTRAL),
    ("W-DOOR", 20.4, 1.3, STRONG_EXT),
    ("CURE-DPO", 16.1, 0.8, OURS),
]


def make_fig1b():
    """Horizontal bars: the labels are long, so rows read better than columns."""
    labels = [r[0] for r in REVERSAL]
    vals = np.array([r[1] for r in REVERSAL])
    errs = np.array([r[2] for r in REVERSAL])
    colors = [r[3] for r in REVERSAL]
    y = np.arange(len(labels))[::-1]

    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, linewidth=0.5)
    ax.barh(
        y, vals, xerr=errs, height=0.64, color=colors, capsize=1.9,
        error_kw={"elinewidth": 0.8, "ecolor": INK},
    )
    for yi, v, e in zip(y, vals, errs):
        ax.text(v + e + 1.1, yi, f"{v:.1f}", ha="left", va="center",
                fontsize=7.0, color=INK)
    ax.axvline(vals[0], color=BASE, lw=0.7, ls=(0, (3, 3)), zorder=1,
               alpha=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.0)
    ax.get_yticklabels()[-1].set_color(OURS)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlabel("Preference reversal (%)")
    ax.set_xlim(0, 58)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_ylim(-0.65, len(labels) - 0.35)
    # 0.435\textwidth, and the height matches fig1a so the two panels of the
    # Figure 1 figure* share a baseline.
    return save_exact(fig, os.path.join(OUT, "fig1b_reversal.pdf"),
                      0.435 * TEXT_WIDTH_IN, 2.289)


# ---------------------------------------------------------------------------
# Figure 3: AUROC forest (4 separations x 6 predictors) + ASR by margin bin.
# ---------------------------------------------------------------------------
PREDICTORS = [
    "LTRM$_{20}$",
    "Min state margin",
    "Mean state margin",
    "Root-response margin",
    "First-token refusal",
    "State depth",
]
REGIMES = ["in-source", "cross-branch", "cross-attack", "fully separated"]
AUROC = {
    "in-source": {
        "LTRM$_{20}$": (0.861, 0.849, 0.873),
        "Min state margin": (0.837, 0.825, 0.850),
        "Mean state margin": (0.814, 0.801, 0.828),
        "Root-response margin": (0.698, 0.682, 0.716),
        "First-token refusal": (0.659, 0.643, 0.677),
        "State depth": (0.596, 0.579, 0.614),
    },
    "cross-branch": {
        "LTRM$_{20}$": (0.831, 0.818, 0.845),
        "Min state margin": (0.811, 0.797, 0.825),
        "Mean state margin": (0.783, 0.769, 0.798),
        "Root-response margin": (0.676, 0.659, 0.694),
        "First-token refusal": (0.642, 0.625, 0.659),
        "State depth": (0.602, 0.585, 0.620),
    },
    "cross-attack": {
        "LTRM$_{20}$": (0.804, 0.791, 0.819),
        "Min state margin": (0.782, 0.767, 0.799),
        "Mean state margin": (0.758, 0.743, 0.775),
        "Root-response margin": (0.654, 0.636, 0.672),
        "First-token refusal": (0.611, 0.594, 0.630),
        "State depth": (0.571, 0.554, 0.590),
    },
    "fully separated": {
        "LTRM$_{20}$": (0.779, 0.764, 0.795),
        "Min state margin": (0.752, 0.736, 0.768),
        "Mean state margin": (0.736, 0.721, 0.753),
        "Root-response margin": (0.648, 0.631, 0.667),
        "First-token refusal": (0.599, 0.581, 0.618),
        "State depth": (0.563, 0.544, 0.583),
    },
}
BIN_X = np.array([-1.25, -0.75, -0.25, 0.25, 0.75, 1.25])
BIN_ASR = np.array([77.1, 63.1, 50.2, 34.8, 22.2, 11.5]) / 100.0
BIN_LO = np.array([72.4, 58.9, 46.7, 31.7, 19.3, 9.0]) / 100.0
BIN_HI = np.array([81.3, 67.0, 53.7, 38.1, 25.4, 14.6]) / 100.0
BIN_N = np.array([341, 547, 763, 861, 721, 513])


def _weighted_logistic(x, p, w):
    """Weighted least squares on the logit; returns a smooth curve."""
    eps = 1e-6
    p = np.clip(p, eps, 1 - eps)
    logit = np.log(p / (1 - p))
    A = np.vstack([np.ones_like(x), x]).T
    W = np.diag(w / w.sum())
    beta = np.linalg.solve(A.T @ W @ A, A.T @ W @ logit)
    xx = np.linspace(x.min() - 0.4, x.max() + 0.4, 240)
    yy = 1.0 / (1.0 + np.exp(-(beta[0] + beta[1] * xx)))
    return xx, yy


def make_fig3():
    fig, (axf, axm) = plt.subplots(
        1, 2, gridspec_kw={"width_ratios": [1.22, 1.0]}
    )

    # (a) AUROC forest ------------------------------------------------------
    ramp = ["#C7D6E6", "#8AA9CC", "#4E7BAC", "#1F4E79"]
    base_y = np.arange(len(PREDICTORS))[::-1]
    offsets = np.linspace(0.30, -0.30, len(REGIMES))
    axf.set_axisbelow(True)
    axf.xaxis.grid(True, linewidth=0.5)
    for i in base_y[1::2]:
        axf.axhspan(i - 0.5, i + 0.5, color="#FAFBFC", zorder=0)
    for ri, reg in enumerate(REGIMES):
        ys = base_y + offsets[ri]
        aur = np.array([AUROC[reg][p][0] for p in PREDICTORS])
        lo = np.array([AUROC[reg][p][1] for p in PREDICTORS])
        hi = np.array([AUROC[reg][p][2] for p in PREDICTORS])
        axf.errorbar(
            aur, ys, xerr=[aur - lo, hi - aur], fmt="o", ms=2.9,
            color=ramp[ri], ecolor=ramp[ri], elinewidth=1.0, capsize=1.4,
            label=reg, zorder=3,
        )
    # Highlight our diagnostic's row.
    axf.axhspan(base_y[0] - 0.5, base_y[0] + 0.5, color=OURS_LT, alpha=0.28,
                zorder=1)
    axf.axvline(0.5, color=MUTED, lw=0.6, ls=(0, (3, 3)), zorder=2)
    axf.set_yticks(base_y)
    axf.set_yticklabels(PREDICTORS, fontsize=7.0)
    axf.get_yticklabels()[0].set_color(OURS)
    axf.get_yticklabels()[0].set_fontweight("bold")
    axf.set_xlim(0.50, 0.90)
    axf.set_ylim(-0.6, len(PREDICTORS) - 0.4)
    axf.set_xlabel("Attack-prediction AUROC")
    axf.legend(loc="lower right", ncol=1, borderpad=0.2)
    axf.set_title("(a) Predictive AUROC under four separations", loc="left",
                  color=INK)

    # (b) ASR by recovery-margin bin ---------------------------------------
    axm.set_axisbelow(True)
    axm.yaxis.grid(True, linewidth=0.5)
    xx, yy = _weighted_logistic(BIN_X, BIN_ASR, BIN_N.astype(float))
    axm.plot(xx, yy, color=EXT, lw=1.3, zorder=2, label="logistic fit")
    sizes = 14 + 52 * (BIN_N / BIN_N.max())
    axm.scatter(BIN_X, BIN_ASR, s=sizes, color=OURS, zorder=4,
                edgecolor="white", linewidth=0.6, label="observed bin")
    # Above the markers: the intervals are narrower than the marker radius, so
    # underneath them only the caps stay visible.
    axm.errorbar(
        BIN_X, BIN_ASR, yerr=[BIN_ASR - BIN_LO, BIN_HI - BIN_ASR], fmt="none",
        ecolor=INK, elinewidth=0.8, capsize=1.8, zorder=5,
    )
    x_lo, x_hi = -1.72, 1.72
    for xi, yi, ni in zip(BIN_X, BIN_ASR, BIN_N):
        # Up and to the right, except near the right edge, where the label would
        # leave the panel; there the empty wedge under the curve is used instead.
        if xi > x_lo + 0.80 * (x_hi - x_lo):
            kw = dict(xytext=(0, -6), ha="center", va="top")
        else:
            kw = dict(xytext=(5, 6), ha="left", va="bottom")
        axm.annotate(f"$n{{=}}{ni}$", (xi, yi), textcoords="offset points",
                     fontsize=7.0, color=MUTED, **kw)
    axm.set_xlabel("Same-state recovery margin")
    axm.set_ylabel("Attack success rate")
    axm.set_ylim(0, 0.92)
    axm.set_xlim(x_lo, x_hi)
    axm.legend(loc="upper right", borderpad=0.2)
    # The separation regime is named in the caption; spelling it out here
    # overruns the panel now that the figure is exactly \textwidth.
    axm.set_title("(b) Attack success by margin bin", loc="left", color=INK)

    return save_exact(fig, os.path.join(OUT, "fig3_diagnostics.pdf"),
                      TEXT_WIDTH_IN, 2.00, w_pad=1.8)


# ---------------------------------------------------------------------------
# Figure 4: attack success vs reached-state depth.
# ---------------------------------------------------------------------------
DEPTHS = np.array([5, 10, 20, 40, 80, 128, 256, 512])
DEPTH_ASR = {
    "Base": [57.7, 58.2, 58.6, 59.0, 59.4, 59.4, 60.4, 74.6],
    "Recovery SFT": [34.8, 36.0, 37.2, 39.0, 40.2, 41.5, 44.0, 48.0],
    "Uniform same-state": [25.8, 26.0, 26.1, 26.2, 26.4, 26.4, 31.0, 44.6],
    "W-DOOR": [21.8, 22.5, 23.0, 23.8, 24.5, 24.8, 29.5, 42.8],
    "CURE-DPO": [18.9, 19.5, 20.2, 20.9, 21.4, 21.4, 23.6, 38.7],
}
DEPTH_STYLE = {
    "Base": (BASE, "o", (0, (1, 0)), 1.4),
    "Recovery SFT": (NEUTRAL_LT, "s", (0, (4, 2)), 1.0),
    "Uniform same-state": (NEUTRAL, "^", (0, (4, 2)), 1.0),
    "W-DOOR": (STRONG_EXT, "D", (0, (4, 2)), 1.1),
    "CURE-DPO": (OURS, "o", (0, (1, 0)), 1.9),
}


def make_fig4():
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linewidth=0.5)
    ax.axvspan(DEPTHS.min(), 80, color="#F1F3F6", zorder=0)
    # The series occupy the middle band, so the shaded-region label sits above
    # them and the legend below them; neither can collide with a curve.
    ax.text(np.sqrt(5 * 80), 76.5, "trained depths ($\\leq$80 tok)",
            ha="center", va="center", fontsize=7.0, color=MUTED)
    # Naming the unshaded half as well: the extrapolation claim is about these
    # depths, and the shading alone only says where training stopped.
    ax.text(np.sqrt(128 * 512), 76.5, "unseen depths", ha="center",
            va="center", fontsize=7.0, color=MUTED)
    for name, ys in DEPTH_ASR.items():
        c, m, ls, lw = DEPTH_STYLE[name]
        ax.plot(DEPTHS, ys, linestyle=ls, color=c, marker=m, ms=2.8, lw=lw,
                markeredgewidth=0, label=name,
                zorder=4 if name == "CURE-DPO" else 3)
    ax.set_xscale("log")
    ax.set_xticks(DEPTHS)
    ax.set_xticklabels(DEPTHS, fontsize=7.0)
    ax.minorticks_off()
    ax.set_xlabel("Reached-state depth (tokens)")
    ax.set_ylabel("Attack success rate (%)")
    ax.set_ylim(0, 80)
    ax.set_xlim(4.4, 620)
    ax.legend(loc="lower left", borderpad=0.2, ncol=2, columnspacing=1.0,
              handletextpad=0.5)
    return save_exact(fig, os.path.join(OUT, "fig4_depth.pdf"),
                      COLUMN_WIDTH_IN, 2.42)


if __name__ == "__main__":
    for fn in (make_fig1a, make_fig1b, make_fig2, make_fig3, make_fig4):
        print("wrote", fn())

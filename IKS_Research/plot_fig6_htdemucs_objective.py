import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Figure 6
# Aggregate objective separation performance of HT-Demucs
#
# IMPORTANT:
# The two groups correspond to DIFFERENT evaluation datasets:
#   Pretrained HT-Demucs -> MUSDB18-Q
#   Fine-tuned HT-Demucs -> held-out SARAGA
#
# They are shown for contextual comparison, NOT as a
# controlled model comparison.
# ============================================================


# -----------------------------
# Data
# -----------------------------

metrics = ["SDR", "SI-SDR", "SIR", "SAR"]

pretrained_vocals = [8.51, 7.68, 18.35, 8.86]
pretrained_accomp = [14.26, 14.19, 22.45, 15.76]

finetuned_vocals = [7.59, 7.13, 16.97, 8.26]
finetuned_accomp = [13.39, 13.06, 19.59, 14.68]


# -----------------------------
# Plot configuration
# -----------------------------

x = np.arange(len(metrics))

group_width = 0.76
bar_width = group_width / 4

fig, ax = plt.subplots(figsize=(7.2, 4.8))


# -----------------------------
# Color palette
# -----------------------------

pretrained_color = "#4C78A8"
finetuned_color = "#F58518"


# -----------------------------
# Bars
# -----------------------------

bars_1 = ax.bar(
    x - 1.5 * bar_width,
    pretrained_vocals,
    width=bar_width,
    color=pretrained_color,
    edgecolor="black",
    linewidth=0.6,
    label="Pretrained · MUSDB18-Q · Vocals"
)

bars_2 = ax.bar(
    x - 0.5 * bar_width,
    pretrained_accomp,
    width=bar_width,
    color=pretrained_color,
    edgecolor="black",
    linewidth=0.6,
    hatch="//",
    label="Pretrained · MUSDB18-Q · Accompaniment"
)

bars_3 = ax.bar(
    x + 0.5 * bar_width,
    finetuned_vocals,
    width=bar_width,
    color=finetuned_color,
    edgecolor="black",
    linewidth=0.6,
    label="Fine-tuned · SARAGA · Vocals"
)

bars_4 = ax.bar(
    x + 1.5 * bar_width,
    finetuned_accomp,
    width=bar_width,
    color=finetuned_color,
    edgecolor="black",
    linewidth=0.6,
    hatch="//",
    label="Fine-tuned · SARAGA · Accompaniment"
)


# -----------------------------
# Value labels
# -----------------------------

for bars in [bars_1, bars_2, bars_3, bars_4]:

    for bar in bars:

        height = bar.get_height()

        ax.annotate(
            f"{height:.2f}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                height
            ),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5
        )


# -----------------------------
# Axes
# -----------------------------

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=10)

ax.set_ylabel(
    "Metric value (dB)",
    fontsize=10
)

ax.set_xlabel(
    "Objective metric",
    fontsize=10
)

ax.set_ylim(0, 25)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.6,
    alpha=0.35
)

ax.set_axisbelow(True)


# -----------------------------
# Legend
# -----------------------------
# The legend is deliberately placed ABOVE the axes so that
# it cannot obscure the SIR bars or their value labels.

ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, 1.02),
    fontsize=7.5,
    frameon=True,
    framealpha=1.0,
    ncol=2,
    columnspacing=1.5,
    handletextpad=0.5
)


# -----------------------------
# Caption-style annotation
# -----------------------------

ax.text(
    0.5,
    -0.22,
    "MUSDB18-Q and SARAGA represent different evaluation conditions; "
    "the results are shown for contextual comparison.",
    transform=ax.transAxes,
    ha="center",
    va="top",
    fontsize=7.5
)


# -----------------------------
# Layout
# -----------------------------
# Leave additional space above the axes for the legend.

plt.subplots_adjust(
    top=0.80,
    bottom=0.22,
    left=0.11,
    right=0.98
)


# -----------------------------
# Save
# -----------------------------

plt.savefig(
    "fig6_htdemucs_objective_results.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
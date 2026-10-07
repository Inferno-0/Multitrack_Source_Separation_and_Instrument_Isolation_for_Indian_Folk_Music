import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Figure 8
# Aggregate controlled TEST performance:
# Banquet baseline vs. Run 002
#
# Left:
#   Global positive-query SDR
#
# Right:
#   Mean negative-query RMS
# ============================================================

# -----------------------------
# Data
# -----------------------------
models = ["Baseline", "Run 002"]

positive_sdr = [2.225, 4.222]
negative_rms = [0.0205, 0.0195]

# -----------------------------
# Plot configuration
# -----------------------------
fig, axes = plt.subplots(
    1,
    2,
    figsize=(7.0, 3.5)
)

x = np.arange(len(models))

bar_colors = ["#7F7F7F", "#2F6DA3"]

# ============================================================
# LEFT PANEL: Positive SDR
# ============================================================

ax = axes[0]

bars = ax.bar(
    x,
    positive_sdr,
    width=0.58,
    color=bar_colors,
    edgecolor="black",
    linewidth=0.7
)

ax.set_title(
    "Positive-query separation",
    fontsize=10,
    pad=8
)

ax.set_ylabel(
    "Mean SDR (dB)",
    fontsize=9
)

ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=9)

ax.set_ylim(0, 5.2)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.6,
    alpha=0.35
)

ax.set_axisbelow(True)

for bar, value in zip(bars, positive_sdr):
    ax.annotate(
        f"{value:.3f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8
    )

# Absolute improvement annotation
ax.annotate(
    "+1.997 dB",
    xy=(1, positive_sdr[1]),
    xytext=(0.5, 4.75),
    ha="center",
    va="center",
    fontsize=8,
    arrowprops=dict(
        arrowstyle="->",
        linewidth=0.8
    )
)

# ============================================================
# RIGHT PANEL: Negative RMS
# ============================================================

ax = axes[1]

bars = ax.bar(
    x,
    negative_rms,
    width=0.58,
    color=bar_colors,
    edgecolor="black",
    linewidth=0.7
)

ax.set_title(
    "Negative-query suppression",
    fontsize=10,
    pad=8
)

ax.set_ylabel(
    "Mean output RMS",
    fontsize=9
)

ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=9)

ax.set_ylim(0, 0.025)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.6,
    alpha=0.35
)

ax.set_axisbelow(True)

for bar, value in zip(bars, negative_rms):
    ax.annotate(
        f"{value:.4f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8
    )

ax.annotate(
    "Lower output",
    xy=(1, negative_rms[1]),
    xytext=(0.55, 0.0225),
    ha="center",
    va="center",
    fontsize=8,
    arrowprops=dict(
        arrowstyle="->",
        linewidth=0.8
    )
)

# -----------------------------
# Overall title
# -----------------------------
fig.suptitle(
    "Controlled TEST performance of Banquet",
    fontsize=11,
    y=1.02
)

# -----------------------------
# Layout
# -----------------------------
plt.tight_layout()

# -----------------------------
# Save
# -----------------------------
plt.savefig(
    "fig8_banquet_test_aggregate.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
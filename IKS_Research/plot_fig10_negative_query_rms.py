import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Figure 10
# Mean negative-query RMS for available instrument classes
# on the controlled TEST evaluation.
#
# Lower RMS = smaller output when the queried instrument
# is absent from the mixture.
# ============================================================

# -----------------------------
# Data
# -----------------------------
instruments = [
    "Tabla",
    "Flute",
    "Dholak",
    "Dhul"
]

baseline_rms = [
    0.0344,
    0.0016,
    0.0293,
    0.0166
]

run002_rms = [
    0.0380,
    0.0015,
    0.0292,
    0.0097
]

x = np.arange(len(instruments))
width = 0.34

# -----------------------------
# Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(6.2, 3.9))

bars_baseline = ax.bar(
    x - width / 2,
    baseline_rms,
    width,
    color="#7F7F7F",
    edgecolor="black",
    linewidth=0.7,
    label="Baseline"
)

bars_run002 = ax.bar(
    x + width / 2,
    run002_rms,
    width,
    color="#2F6DA3",
    edgecolor="black",
    linewidth=0.7,
    label="Run 002"
)

# -----------------------------
# Value labels
# -----------------------------
for bar, value in zip(bars_baseline, baseline_rms):
    ax.annotate(
        f"{value:.4f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=7.5
    )

for bar, value in zip(bars_run002, run002_rms):
    ax.annotate(
        f"{value:.4f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
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
ax.set_xticklabels(
    instruments,
    fontsize=9.5
)

ax.set_ylabel(
    "Mean negative-query RMS",
    fontsize=10
)

ax.set_xlabel(
    "Instrument query",
    fontsize=10
)

ax.set_ylim(0, 0.043)

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
ax.legend(
    loc="upper right",
    fontsize=8.5,
    frameon=True
)

# -----------------------------
# Interpretation note
# -----------------------------
ax.text(
    0.5,
    -0.24,
    "Lower values indicate smaller output when the queried instrument is absent.",
    transform=ax.transAxes,
    ha="center",
    va="top",
    fontsize=7.5
)

# -----------------------------
# Layout
# -----------------------------
plt.tight_layout()

# -----------------------------
# Save
# -----------------------------
plt.savefig(
    "fig10_negative_query_rms.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
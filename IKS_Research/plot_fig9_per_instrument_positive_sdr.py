import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Figure 9
# Available per-instrument positive-query SDR on the
# independent TEST set
# ============================================================

# Only instruments with valid positive TEST cases are included.
instruments = ["Tabla", "Flute"]

baseline_sdr = np.array([
    0.909,
    3.421
])

run002_sdr = np.array([
    0.857,
    7.281
])

x = np.arange(len(instruments))
width = 0.34

fig, ax = plt.subplots(figsize=(8.5, 5.5))

# Baseline and fine-tuned results
bars_baseline = ax.bar(
    x - width / 2,
    baseline_sdr,
    width,
    label="Banquet baseline"
)

bars_run002 = ax.bar(
    x + width / 2,
    run002_sdr,
    width,
    label="Run 002"
)

# Axis labels and title
ax.set_xlabel("Instrument", fontsize=13)
ax.set_ylabel("Positive-query SDR (dB)", fontsize=13)

ax.set_xticks(x)
ax.set_xticklabels(instruments, fontsize=12)

ax.tick_params(axis="y", labelsize=11)

# Light horizontal grid
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.8,
    alpha=0.35
)

ax.set_axisbelow(True)

# Add numerical values above bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10
        )

add_labels(bars_baseline)
add_labels(bars_run002)

# Legend
ax.legend(
    loc="upper left",
    frameon=False,
    fontsize=11
)

# Give the bars some vertical breathing room
ax.set_ylim(0, max(run002_sdr) * 1.22)

# Clean up unnecessary top/right borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()

# Save publication-quality PNG
plt.savefig(
    "fig9_per_instrument_positive_sdr.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
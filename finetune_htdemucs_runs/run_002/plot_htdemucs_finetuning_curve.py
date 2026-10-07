import re
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

TRAIN_LOG = "train_log.txt"
VALID_LOG = "valid_log.txt"

OUTPUT_FILE = "htdemucs_finetuning_loss_curve.png"

MAX_STEP = 15000
WINDOW = 500


# ============================================================
# Parse training log
# ============================================================

train_steps = []
train_losses = []

train_pattern = re.compile(
    r"step=(\d+)\s+loss=([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
)

with open(TRAIN_LOG, "r", encoding="utf-8") as f:
    for line in f:
        match = train_pattern.search(line)

        if match:
            step = int(match.group(1))
            loss = float(match.group(2))

            if step <= MAX_STEP:
                train_steps.append(step)
                train_losses.append(loss)


# ============================================================
# Parse validation log
# ============================================================

valid_steps = []
valid_losses = []

valid_pattern = re.compile(
    r"step=(\d+).*?(?:loss|val_loss)=([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
)

with open(VALID_LOG, "r", encoding="utf-8") as f:
    for line in f:
        match = valid_pattern.search(line)

        if match:
            step = int(match.group(1))
            loss = float(match.group(2))

            if step <= MAX_STEP:
                valid_steps.append(step)
                valid_losses.append(loss)


# ============================================================
# Convert to NumPy arrays
# ============================================================

train_steps = np.asarray(train_steps)
train_losses = np.asarray(train_losses)

valid_steps = np.asarray(valid_steps)
valid_losses = np.asarray(valid_losses)


# ============================================================
# Calculate 500-step training-loss averages
#
# IMPORTANT:
# These are block averages, not raw losses.
# Each point represents the mean training L1 over
# a 500-step interval.
# ============================================================

avg_train_steps = []
avg_train_losses = []

for start in range(1, MAX_STEP + 1, WINDOW):

    end = min(start + WINDOW - 1, MAX_STEP)

    mask = (train_steps >= start) & (train_steps <= end)

    if np.any(mask):
        avg_train_steps.append(
            np.mean(train_steps[mask])
        )

        avg_train_losses.append(
            np.mean(train_losses[mask])
        )


avg_train_steps = np.asarray(avg_train_steps)
avg_train_losses = np.asarray(avg_train_losses)


# ============================================================
# Determine best validation point
# ============================================================

best_idx = np.argmin(valid_losses)

best_valid_step = valid_steps[best_idx]
best_valid_loss = valid_losses[best_idx]


# ============================================================
# Print useful verification information
# ============================================================

print("Training samples:", len(train_losses))
print("Validation samples:", len(valid_losses))

print(
    f"Best validation L1 = {best_valid_loss:.9f} "
    f"at step {best_valid_step}"
)

print(
    f"Final raw training L1 = "
    f"{train_losses[-1]:.6f} "
    f"at step {train_steps[-1]}"
)

print(
    f"Final 500-step average training L1 = "
    f"{avg_train_losses[-1]:.6f}"
)


# ============================================================
# Create figure
# ============================================================

fig, ax = plt.subplots(figsize=(12, 7.5))


# Training curve
ax.plot(
    avg_train_steps,
    avg_train_losses,
    linewidth=2.8,
    label="Training L1 (500-step average)"
)


# Validation curve
ax.plot(
    valid_steps,
    valid_losses,
    linewidth=2.8,
    marker="o",
    markersize=6,
    label="Validation L1"
)


# ============================================================
# Highlight best validation point
# ============================================================

validation_color = ax.lines[1].get_color()

ax.scatter(
    [best_valid_step],
    [best_valid_loss],
    s=130,
    color=validation_color,
    edgecolors="black",
    linewidths=1.2,
    zorder=5
)


# Annotation
ax.annotate(
    f"Best validation L1 = {best_valid_loss:.6f}",
    xy=(best_valid_step, best_valid_loss),
    xytext=(9500, 0.00485),
    fontsize=14,
    arrowprops=dict(
        arrowstyle="->",
        linewidth=1.5
    )
)


# ============================================================
# Axis labels
# ============================================================

ax.set_xlabel(
    "Optimizer Step",
    fontsize=18
)

ax.set_ylabel(
    "L1 Loss",
    fontsize=18
)


# ============================================================
# Axis limits and ticks
# ============================================================

ax.set_xlim(0, MAX_STEP)

ax.set_xticks(
    [0, 2500, 5000, 7500, 10000, 12500, 15000]
)

ax.tick_params(
    axis="both",
    labelsize=14
)


# ============================================================
# Grid
# ============================================================

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


# ============================================================
# Legend
# ============================================================

ax.legend(
    fontsize=15,
    loc="upper right",
    frameon=False
)


# ============================================================
# Layout
# ============================================================

plt.tight_layout()


# ============================================================
# Save high-resolution PNG
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"\nFigure saved as: {OUTPUT_FILE}")
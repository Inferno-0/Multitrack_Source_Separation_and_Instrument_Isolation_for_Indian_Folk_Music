"""
generate_plots.py

Generates all evaluation plots for the fine-tuned HT-Demucs model evaluation.
All plots are generated from saved CSV data and actual fine-tuning logs.

Plots produced:
  plots/training_validation_loss_curve.png
  plots/per_track_SDR.png
  plots/per_track_SI_SDR.png
  plots/per_track_SAR.png
  plots/per_track_SIR.png
  plots/metric_distribution_summary.png
  plots/source_wise_metric_summary.png

Usage: C:\\iks_scripts\\venv\\Scripts\\python.exe generate_plots.py
"""

import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

EVAL_ROOT  = r"D:\IKS_Research\FineTuned_Evaluation"
PLOTS_DIR  = os.path.join(EVAL_ROOT, "plots")
TABLES_DIR = os.path.join(EVAL_ROOT, "tables")
TRAIN_LOG  = r"D:\finetune_htdemucs_runs\run_002\train_log.txt"
VALID_LOG  = r"D:\finetune_htdemucs_runs\run_002\valid_log.txt"

SOURCES    = ["vocals", "accompaniment"]
METRICS    = ["SDR", "SI_SDR", "SIR", "SAR"]
METRIC_LABELS = {"SDR": "SDR (dB)", "SI_SDR": "SI-SDR (dB)",
                 "SIR": "SIR (dB)", "SAR": "SAR (dB)"}

COLORS = {"vocals": "#4C72B0", "accompaniment": "#DD8452"}
DPI    = 150

os.makedirs(PLOTS_DIR, exist_ok=True)


# ── Load per-track CSV ────────────────────────────────────────────────────────
def load_per_track():
    rows = []
    with open(os.path.join(TABLES_DIR, "per_track_metrics.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "track_name": r["track_name"],
                "source": r["source"],
                "SDR":    float(r["SDR"]),
                "SI_SDR": float(r["SI_SDR"]),
                "SIR":    float(r["SIR"]),
                "SAR":    float(r["SAR"]),
            })
    return rows


def get_vals(rows, src, metric):
    return [r[metric] for r in rows if r["source"] == src]


def get_tracks(rows):
    seen = []
    for r in rows:
        if r["track_name"] not in seen:
            seen.append(r["track_name"])
    return seen


# ── 1. Training / Validation Loss Curve ──────────────────────────────────────
def plot_loss_curve():
    # Parse train log
    train_steps, train_losses = [], []
    with open(TRAIN_LOG, encoding="utf-8") as f:
        for line in f:
            parts = {kv.split("=")[0]: kv.split("=")[1]
                     for kv in line.strip().split() if "=" in kv}
            if "step" in parts and "loss" in parts:
                try:
                    train_steps.append(int(parts["step"]))
                    train_losses.append(float(parts["loss"]))
                except ValueError:
                    pass

    # Smooth training curve (rolling mean, window=200)
    window = 200
    smoothed = np.convolve(train_losses, np.ones(window)/window, mode="valid")
    smooth_steps = train_steps[window-1:]

    # Parse valid log
    valid_steps, valid_losses = [], []
    with open(VALID_LOG, encoding="utf-8") as f:
        for line in f:
            parts = {kv.split("=")[0]: kv.split("=")[1]
                     for kv in line.strip().split() if "=" in kv}
            if "step" in parts and "valid_l1_loss" in parts:
                try:
                    valid_steps.append(int(parts["step"]))
                    valid_losses.append(float(parts["valid_l1_loss"]))
                except ValueError:
                    pass

    best_step = valid_steps[valid_losses.index(min(valid_losses))]
    best_loss = min(valid_losses)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(train_steps, train_losses, color="#aec6e8", alpha=0.35,
            linewidth=0.6, label="Training L1 loss (raw)")
    ax.plot(smooth_steps, smoothed, color="#2171b5", linewidth=1.8,
            label=f"Training L1 loss (smoothed, window={window})")
    ax.plot(valid_steps, valid_losses, color="#e6550d", linewidth=2.2,
            marker="o", markersize=4, label="Validation L1 loss")
    ax.scatter([best_step], [best_loss], color="#e6550d", s=100, zorder=5)
    ax.annotate(f"Best val = {best_loss:.5f}\n(step {best_step:,})",
                xy=(best_step, best_loss),
                xytext=(best_step - 2800, best_loss + 0.0008),
                fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2),
                color="#333333")
    ax.set_xlabel("Optimizer Step", fontsize=11)
    ax.set_ylabel("L1 Loss", fontsize=11)
    ax.set_title("HT-Demucs 2-Stem Fine-Tuning: Training & Validation Loss",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=9)
    ax.set_xlim(0, max(train_steps) + 200)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "training_validation_loss_curve.png")
    plt.savefig(out, dpi=DPI)
    plt.close()
    print(f"Wrote: {out}")


# ── 2-5. Per-track metric plots ───────────────────────────────────────────────
def plot_per_track(rows, metric):
    tracks = get_tracks(rows)
    short_names = [t.replace("saraga_", "#") for t in tracks]
    x = np.arange(len(tracks))
    w = 0.35

    v_vals = get_vals(rows, "vocals", metric)
    a_vals = get_vals(rows, "accompaniment", metric)

    fig, ax = plt.subplots(figsize=(14, 5))
    bars1 = ax.bar(x - w/2, v_vals, w, label="Vocals",
                   color=COLORS["vocals"], alpha=0.85)
    bars2 = ax.bar(x + w/2, a_vals, w, label="Accompaniment",
                   color=COLORS["accompaniment"], alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(short_names, fontsize=8.5, rotation=30, ha="right")
    ax.set_xlabel("Validation Track", fontsize=11)
    ax.set_ylabel(METRIC_LABELS[metric], fontsize=11)
    ax.set_title(f"Per-Track {metric.replace('_', '-')} — Fine-Tuned HT-Demucs",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)

    # Mean lines
    ax.axhline(np.mean(v_vals), color=COLORS["vocals"],
               linestyle="--", linewidth=1.2,
               label=f"Vocals mean = {np.mean(v_vals):.2f}")
    ax.axhline(np.mean(a_vals), color=COLORS["accompaniment"],
               linestyle="--", linewidth=1.2,
               label=f"Accompaniment mean = {np.mean(a_vals):.2f}")
    ax.legend(fontsize=9)
    plt.tight_layout()
    fname = f"per_track_{metric}.png"
    out = os.path.join(PLOTS_DIR, fname)
    plt.savefig(out, dpi=DPI)
    plt.close()
    print(f"Wrote: {out}")


# ── 6. Metric distribution (boxplots) ────────────────────────────────────────
def plot_distributions(rows):
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    for ax, metric in zip(axes, METRICS):
        v_vals = get_vals(rows, "vocals", metric)
        a_vals = get_vals(rows, "accompaniment", metric)
        bp = ax.boxplot(
            [v_vals, a_vals],
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            whiskerprops=dict(linewidth=1.2),
            capprops=dict(linewidth=1.2),
        )
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["Vocals", "Accompaniment"])
        bp["boxes"][0].set_facecolor(COLORS["vocals"])
        bp["boxes"][0].set_alpha(0.8)
        bp["boxes"][1].set_facecolor(COLORS["accompaniment"])
        bp["boxes"][1].set_alpha(0.8)
        ax.set_title(metric.replace("_", "-"), fontsize=11, fontweight="bold")
        ax.set_ylabel("dB", fontsize=10)
        ax.grid(True, axis="y", alpha=0.3)
    fig.suptitle("Metric Distributions — Fine-Tuned HT-Demucs (15 validation tracks)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "metric_distribution_summary.png")
    plt.savefig(out, dpi=DPI)
    plt.close()
    print(f"Wrote: {out}")


# ── 7. Source-wise aggregate comparison ──────────────────────────────────────
def plot_source_aggregate(rows):
    means = {
        src: {m: np.mean(get_vals(rows, src, m)) for m in METRICS}
        for src in SOURCES
    }
    stds = {
        src: {m: np.std(get_vals(rows, src, m)) for m in METRICS}
        for src in SOURCES
    }

    x     = np.arange(len(METRICS))
    w     = 0.3
    xlabels = [m.replace("_", "-") for m in METRICS]

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, src in enumerate(SOURCES):
        vals  = [means[src][m] for m in METRICS]
        errs  = [stds[src][m]  for m in METRICS]
        offset = (i - 0.5) * w
        ax.bar(x + offset, vals, w,
               label=src.capitalize(), color=COLORS[src], alpha=0.85,
               yerr=errs, error_kw=dict(elinewidth=1.2, capsize=4))

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=12)
    ax.set_ylabel("Mean ± Std (dB)", fontsize=11)
    ax.set_title("Source-Wise Aggregate Metrics — Fine-Tuned HT-Demucs",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "source_wise_metric_summary.png")
    plt.savefig(out, dpi=DPI)
    plt.close()
    print(f"Wrote: {out}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Loading per-track metrics...")
    rows = load_per_track()
    print(f"  Loaded {len(rows)} rows ({len(rows)//2} tracks x 2 sources)")

    print("\nGenerating plots...")
    plot_loss_curve()
    for m in METRICS:
        plot_per_track(rows, m)
    plot_distributions(rows)
    plot_source_aggregate(rows)

    print("\nAll plots written to:", PLOTS_DIR)

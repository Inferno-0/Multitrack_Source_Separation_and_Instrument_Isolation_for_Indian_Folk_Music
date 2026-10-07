import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ============================================================
# HT-DEMUCS ARCHITECTURE FIGURE (FIGURE 3)
# ============================================================

def create_architecture_figure():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # --------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-0.5, 10.5)
    ax.axis("off")

    # --------------------------------------------------------
    # PROFESSIONAL RESEARCH-PAPER PALETTE
    # --------------------------------------------------------
    NAVY        = "#173856"
    NAVY_FILL   = "#E4EAEF"

    TEAL        = "#1C6166"
    TEAL_FILL   = "#E0EEEF"

    ORANGE      = "#8C6023"
    ORANGE_FILL = "#F6EEE3"

    GREEN       = "#28513B"
    GREEN_FILL  = "#E6EDE9"

    DARK_GREY   = "#555555"
    MID_GREY    = "#777777"
    TEXT_COLOR  = "#222222"

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------
    def add_box(x, y, w, h, text, ec, fc, tc, fsize=11, weight="bold"):
        patch = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.04,rounding_size=0.1",
            linewidth=1.25,
            edgecolor=ec,
            facecolor=fc,
            zorder=3
        )
        ax.add_patch(patch)
        
        if text:
            ax.text(x, y, text, ha="center", va="center", 
                    fontsize=fsize, fontweight=weight, family="serif", color=tc, zorder=4)

    def draw_ortho_arrow(points, color=DARK_GREY, lw=1.4, ls="-"):
        if len(points) > 2:
            xs = [p[0] for p in points[:-1]]
            ys = [p[1] for p in points[:-1]]
            ax.plot(xs, ys, color=color, lw=lw, linestyle=ls, zorder=1)
        
        ax.annotate('', xy=points[-1], xytext=points[-2],
                    arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.4", 
                                    color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0),
                    zorder=2)

    # ========================================================
    # NODES & GROUPING LABELS
    # ========================================================

    # Domain Headers
    ax.text(-3.0, 10.2, "TIME DOMAIN", ha="center", va="center", 
            fontsize=9, fontweight="bold", family="serif", color=MID_GREY)
    ax.text(3.0, 10.2, "FREQUENCY DOMAIN", ha="center", va="center", 
            fontsize=9, fontweight="bold", family="serif", color=MID_GREY)

    # Input
    ax.text(0, 9.8, "Input Mixture", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=TEXT_COLOR)

    # Encoders
    add_box(-3.0, 8.0, 4.2, 1.0, "Waveform Encoder", NAVY, NAVY_FILL, NAVY)
    add_box(3.0, 8.0, 4.2, 1.0, "Spectrogram Encoder", TEAL, TEAL_FILL, TEAL)

    # Feature Labels (in the gaps)
    ax.text(-3.0, 6.55, "Time-Domain Features", ha="center", va="center", 
            fontsize=10, family="serif", color=DARK_GREY)
    ax.text(3.0, 6.55, "Time-Frequency Features", ha="center", va="center", 
            fontsize=10, family="serif", color=DARK_GREY)

    # Transformer (spanning both domains)
    add_box(0, 4.8, 8.4, 1.6, "", ORANGE, ORANGE_FILL, ORANGE)
    ax.text(0, 5.15, "Cross-Domain\nTransformer", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=ORANGE)
    ax.text(0, 4.3, "Joint temporal / spectral\nrepresentation", ha="center", va="center", 
            fontsize=10, family="serif", color=ORANGE)
            
    # Bidirectional cross-domain interaction arrow
    ax.annotate('', xy=(-1.8, 4.75), xytext=(1.8, 4.75),
                arrowprops=dict(arrowstyle="<|-|>,head_length=0.5,head_width=0.35", 
                                color=ORANGE, lw=1.2), zorder=4)

    # Decoders
    add_box(-3.0, 2.0, 4.2, 1.0, "Waveform Decoder", NAVY, NAVY_FILL, NAVY)
    add_box(3.0, 2.0, 4.2, 1.0, "Spectrogram Decoder", TEAL, TEAL_FILL, TEAL)

    # Output
    ax.text(0, 0.3, "Source Estimates\nVocals + Accompaniment", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=TEXT_COLOR)

    # ========================================================
    # CONNECTIONS
    # ========================================================

    # Input to Encoders
    ax.plot([0, 0], [9.5, 9.0], color=DARK_GREY, lw=1.4, zorder=1)
    ax.plot([-3.0, 3.0], [9.0, 9.0], color=DARK_GREY, lw=1.4, zorder=1)
    draw_ortho_arrow([(-3.0, 9.0), (-3.0, 8.5)])
    draw_ortho_arrow([(3.0, 9.0), (3.0, 8.5)])

    # Encoders to Transformer (with gaps for feature labels)
    ax.plot([-3.0, -3.0], [7.5, 6.8], color=DARK_GREY, lw=1.4, zorder=1)
    draw_ortho_arrow([(-3.0, 6.3), (-3.0, 5.6)])
    
    ax.plot([3.0, 3.0], [7.5, 6.8], color=DARK_GREY, lw=1.4, zorder=1)
    draw_ortho_arrow([(3.0, 6.3), (3.0, 5.6)])

    # Transformer to Decoders
    draw_ortho_arrow([(-3.0, 4.0), (-3.0, 2.5)])
    draw_ortho_arrow([(3.0, 4.0), (3.0, 2.5)])

    # Decoders to Output
    ax.plot([-3.0, -3.0], [1.5, 1.0], color=DARK_GREY, lw=1.4, zorder=1)
    ax.plot([3.0, 3.0], [1.5, 1.0], color=DARK_GREY, lw=1.4, zorder=1)
    ax.plot([-3.0, 3.0], [1.0, 1.0], color=DARK_GREY, lw=1.4, zorder=1)
    draw_ortho_arrow([(0, 1.0), (0, 0.7)])

    # ========================================================
    # SKIP CONNECTIONS
    # ========================================================
    
    # Waveform Skip
    ax.plot([-5.1, -5.8], [8.0, 8.0], color=MID_GREY, lw=1.2, linestyle="--", zorder=1)
    ax.plot([-5.8, -5.8], [8.0, 2.0], color=MID_GREY, lw=1.2, linestyle="--", zorder=1)
    draw_ortho_arrow([(-5.8, 2.0), (-5.1, 2.0)], color=MID_GREY, lw=1.2, ls="--")

    # Spectrogram Skip
    ax.plot([5.1, 5.8], [8.0, 8.0], color=MID_GREY, lw=1.2, linestyle="--", zorder=1)
    ax.plot([5.8, 5.8], [8.0, 2.0], color=MID_GREY, lw=1.2, linestyle="--", zorder=1)
    draw_ortho_arrow([(5.8, 2.0), (5.1, 2.0)], color=MID_GREY, lw=1.2, ls="--")

    # ========================================================
    # FINAL FORMATTING & SAVE
    # ========================================================
    plt.tight_layout()
    output_path = os.path.join(os.getcwd(), "ht_demucs_architecture.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"PNG saved at: {output_path}")

if __name__ == "__main__":
    create_architecture_figure()

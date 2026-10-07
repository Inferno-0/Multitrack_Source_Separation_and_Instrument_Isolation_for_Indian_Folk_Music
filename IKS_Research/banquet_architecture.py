import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ============================================================
# BANQUET ARCHITECTURE FIGURE (FIGURE 5)
# ============================================================

def create_architecture_figure():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # --------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(0, 10.5)
    ax.axis("off")

    # --------------------------------------------------------
    # PROFESSIONAL RESEARCH-PAPER PALETTE
    # --------------------------------------------------------
    NAVY       = "#355C8A"
    NAVY_FILL  = "#DCE6F1"
    
    TEAL       = "#3D7F7B"
    TEAL_FILL  = "#D9EAE8"
    
    ORANGE     = "#B86B2C"
    ORANGE_FILL = "#F1E1D2"
    
    DARK_GREY  = "#333333"
    MID_GREY   = "#666666"
    TEXT_COLOR = "#1F1F1F"

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------
    def add_box(x, y, w, h, text, ec, fc, tc, fsize=11, weight="bold"):
        patch = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.04,rounding_size=0.1",
            linewidth=1.4,
            edgecolor=ec,
            facecolor=fc,
            zorder=3
        )
        ax.add_patch(patch)
        
        if text:
            ax.text(x, y, text, ha="center", va="center", 
                    fontsize=fsize, fontweight=weight, family="serif", color=tc, zorder=4)

    def draw_ortho_arrow(points, color=DARK_GREY, lw=1.5, ls="-"):
        if len(points) > 2:
            xs = [p[0] for p in points[:-1]]
            ys = [p[1] for p in points[:-1]]
            ax.plot(xs, ys, color=color, lw=lw, linestyle=ls, zorder=1)
        
        ax.annotate('', xy=points[-1], xytext=points[-2],
                    arrowprops=dict(arrowstyle="-|>,head_length=0.65,head_width=0.45", 
                                    color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0),
                    zorder=2)

    # ========================================================
    # LAYOUT PARAMETERS
    # ========================================================
    X_MIX = -3.0
    X_QRY = 3.0
    
    BW = 4.0
    BH = 1.1

    # ========================================================
    # NODES & GROUPING LABELS
    # ========================================================

    # Path Headers
    ax.text(X_MIX, 10.1, "MIXTURE PATH", ha="center", va="center", 
            fontsize=9, fontweight="bold", family="serif", color=MID_GREY)
    ax.text(X_QRY, 10.1, "QUERY PATH", ha="center", va="center", 
            fontsize=9, fontweight="bold", family="serif", color=MID_GREY)

    # --------------------------------------------------------
    # MIXTURE PATH (Left)
    # --------------------------------------------------------
    ax.text(X_MIX, 9.2, "Audio Mixture", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=TEXT_COLOR)
            
    add_box(X_MIX, 7.6, BW, BH, "Mixture Encoder", NAVY, NAVY_FILL, NAVY)
    
    add_box(X_MIX, 5.8, BW, BH, "Latent Mixture\nRepresentation", NAVY, NAVY_FILL, NAVY)
    
    add_box(X_MIX, 4.0, BW, BH, "FiLM\nConditioning", ORANGE, ORANGE_FILL, ORANGE)
    
    add_box(X_MIX, 2.2, BW, BH, "Separation\nDecoder", NAVY, NAVY_FILL, NAVY)
    
    ax.text(X_MIX, 0.7, "Target Estimate", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=TEXT_COLOR)

    # --------------------------------------------------------
    # QUERY PATH (Right)
    # --------------------------------------------------------
    ax.text(X_QRY, 9.2, "Audio Query", ha="center", va="center", 
            fontsize=12, fontweight="bold", family="serif", color=TEXT_COLOR)
            
    add_box(X_QRY, 7.6, BW, BH, "Query Preprocessing\nMono + Resampling", TEAL, TEAL_FILL, TEAL)
    
    add_box(X_QRY, 5.8, BW, BH, "PaSST-based\nQuery Encoder", TEAL, TEAL_FILL, TEAL)
    
    add_box(X_QRY, 4.0, BW, BH, "Query Embedding", TEAL, TEAL_FILL, TEAL)

    # --------------------------------------------------------
    # ANNOTATIONS
    # --------------------------------------------------------
    # Near FiLM block
    ax.text(0.0, 4.25, "Query-dependent modulation", ha="center", va="center", 
            fontsize=9.5, family="serif", color=DARK_GREY, style="italic")
            
    # Near Query Encoder
    ax.text(X_QRY + 2.3, 5.8, "Target-source\nrepresentation", ha="left", va="center", 
            fontsize=9.5, family="serif", color=DARK_GREY, style="italic")

    # ========================================================
    # CONNECTIONS
    # ========================================================

    # Mixture Path
    draw_ortho_arrow([(X_MIX, 8.9), (X_MIX, 8.15)])
    draw_ortho_arrow([(X_MIX, 7.05), (X_MIX, 6.35)])
    draw_ortho_arrow([(X_MIX, 5.25), (X_MIX, 4.55)])
    draw_ortho_arrow([(X_MIX, 3.45), (X_MIX, 2.75)])
    draw_ortho_arrow([(X_MIX, 1.65), (X_MIX, 1.0)])

    # Query Path
    draw_ortho_arrow([(X_QRY, 8.9), (X_QRY, 8.15)])
    draw_ortho_arrow([(X_QRY, 7.05), (X_QRY, 6.35)])
    draw_ortho_arrow([(X_QRY, 5.25), (X_QRY, 4.55)])
    
    # Query Embedding -> FiLM Conditioning (Horizontal)
    draw_ortho_arrow([(X_QRY - 2.0, 4.0), (X_MIX + 2.0, 4.0)], color=ORANGE, lw=1.6)

    # ========================================================
    # FINAL FORMATTING & SAVE
    # ========================================================
    plt.tight_layout()
    output_path = os.path.join(os.getcwd(), "banquet_architecture.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"PNG saved at: {output_path}")

if __name__ == "__main__":
    create_architecture_figure()

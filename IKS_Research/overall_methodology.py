import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ============================================================
# OVERALL METHODOLOGY FIGURE
# ============================================================

def create_overall_methodology():
    fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # --------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-0.5, 12)
    ax.axis("off")

    # --------------------------------------------------------
    # PROFESSIONAL RESEARCH-PAPER PALETTE
    # --------------------------------------------------------
    ARROW_COLOR = "#707070"
    TEXT_COLOR = "#222222"
    ANNOTATION_COLOR = "#606060"

    # Instrument-Level Track / blue
    BLUE_EC = "#315A85"
    BLUE_FC = "#EEF3F8"
    BLUE_TC = "#183B63"

    # Audio Preparation / teal
    TEAL_EC = "#3A7D78"
    TEAL_FC = "#EEF6F4"
    TEAL_TC = "#245C58"

    # Pretrained Model / evaluation / orange
    ORANGE_EC = "#B87935"
    ORANGE_FC = "#FBF4EA"
    ORANGE_TC = "#8A4F12"

    # Baseline Track / green
    GREEN_EC = "#4F8054"
    GREEN_FC = "#EFF5EF"
    GREEN_TC = "#356039"

    # Adaptation Track / purple
    PURPLE_EC = "#705587"
    PURPLE_FC = "#F3EEF6"
    PURPLE_TC = "#573C6C"

    # --------------------------------------------------------
    # BOX PARAMETERS
    # --------------------------------------------------------
    BOX_W = 3.35
    BOX_H = 0.86

    # --------------------------------------------------------
    # BOX FUNCTION
    # --------------------------------------------------------
    boxes = {}

    def add_box(name, x, y, text, ec, fc, tc):
        patch = FancyBboxPatch(
            (x - BOX_W / 2, y - BOX_H / 2),
            BOX_W,
            BOX_H,
            boxstyle="round,pad=0.045,rounding_size=0.08",
            linewidth=1.1,
            edgecolor=ec,
            facecolor=fc,
            zorder=3
        )
        ax.add_patch(patch)

        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            family="serif",
            color=tc,
            zorder=4
        )
        boxes[name] = {"x": x, "y": y}

    # --------------------------------------------------------
    # EDGE POINT HELPERS
    # --------------------------------------------------------
    def top(name):
        return (boxes[name]["x"], boxes[name]["y"] + BOX_H / 2)

    def bottom(name):
        return (boxes[name]["x"], boxes[name]["y"] - BOX_H / 2)

    def left(name):
        return (boxes[name]["x"] - BOX_W / 2, boxes[name]["y"])

    def right(name):
        return (boxes[name]["x"] + BOX_W / 2, boxes[name]["y"])

    # --------------------------------------------------------
    # ARROW FUNCTION (ORTHOGONAL ROUTING)
    # --------------------------------------------------------
    def draw_ortho_arrow(points):
        if len(points) > 2:
            xs = [p[0] for p in points[:-1]]
            ys = [p[1] for p in points[:-1]]
            ax.plot(xs, ys, color=ARROW_COLOR, lw=1.15, zorder=1)
        
        ax.annotate('', xy=points[-1], xytext=points[-2],
                    arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.4", 
                                    color=ARROW_COLOR, lw=1.15, shrinkA=0, shrinkB=0),
                    zorder=2)

    # ========================================================
    # NODES
    # ========================================================

    # TOP COMMON PIPELINE (Center: x=0)
    add_box("corpus", 0, 11.0, "Indian Folk Corpus", BLUE_EC, BLUE_FC, BLUE_TC)
    add_box("prep", 0, 9.5, "Audio Preparation", TEAL_EC, TEAL_FC, TEAL_TC)
    add_box("pretrained", 0, 8.0, "Pretrained HT-Demucs", ORANGE_EC, ORANGE_FC, ORANGE_TC)

    # BASELINE TRACK (Left: x=-4.0)
    add_box("baseline", -4.0, 6.5, "Two-Stem Baseline", GREEN_EC, GREEN_FC, GREEN_TC)
    
    # INSTRUMENT-LEVEL TRACK (Center: x=0)
    add_box("isolated", 0, 5.0, "Isolated Instrument Data", BLUE_EC, BLUE_FC, BLUE_TC)
    add_box("banquet", 0, 3.5, "Query-Conditioned Banquet", BLUE_EC, BLUE_FC, BLUE_TC)
    add_box("controlled", 0, 2.0, "Controlled\nInstrument Separation", BLUE_EC, BLUE_FC, BLUE_TC)

    # ADAPTATION TRACK (Right: x=4.0)
    add_box("saraga", 4.0, 6.5, "SARAGA Dataset", PURPLE_EC, PURPLE_FC, PURPLE_TC)
    add_box("finetuned", 4.0, 5.0, "Fine-Tuned HT-Demucs", PURPLE_EC, PURPLE_FC, PURPLE_TC)

    # FINAL EVALUATION (Center: x=0)
    add_box("evaluation", 0, 0.5, "Independent Evaluation", ORANGE_EC, ORANGE_FC, ORANGE_TC)

    # ========================================================
    # CONNECTIONS
    # ========================================================

    # Common Pipeline
    draw_ortho_arrow([bottom("corpus"), top("prep")])
    draw_ortho_arrow([bottom("prep"), top("pretrained")])

    # Pretrained -> Two-Stem Baseline
    draw_ortho_arrow([left("pretrained"), (-4.0, 8.0), top("baseline")])
    
    # Pretrained -> Isolated Instrument Data (with gap for label)
    ax.plot([0, 0], [bottom("pretrained")[1], 6.7], color=ARROW_COLOR, lw=1.15, zorder=1)
    draw_ortho_arrow([(0, 6.3), top("isolated")])

    # Pretrained -> SARAGA Dataset
    draw_ortho_arrow([right("pretrained"), (4.0, 8.0), top("saraga")])

    # Pretrained -> Fine-Tuned (Initialization)
    draw_ortho_arrow([(1.5, 7.7), (2.2, 7.7), (2.2, 5.0), left("finetuned")])

    # Instrument-Level Track internal
    draw_ortho_arrow([bottom("isolated"), top("banquet")])
    draw_ortho_arrow([bottom("banquet"), top("controlled")])

    # Adaptation Track internal
    draw_ortho_arrow([bottom("saraga"), top("finetuned")])

    # To Independent Evaluation
    draw_ortho_arrow([bottom("baseline"), (-4.0, 0.5), left("evaluation")])
    draw_ortho_arrow([bottom("controlled"), top("evaluation")])
    draw_ortho_arrow([bottom("finetuned"), (4.0, 0.5), right("evaluation")])

    # ========================================================
    # TRACK LABELS
    # ========================================================

    ax.text(-4.0, 8.6, "Baseline Track", ha="center", va="center", 
            fontsize=10.5, fontweight="bold", family="serif", color=GREEN_TC)
            
    ax.text(0, 6.5, "Instrument-Level Track", ha="center", va="center", 
            fontsize=10.5, fontweight="bold", family="serif", color=BLUE_TC)
            
    ax.text(4.0, 8.6, "Adaptation Track", ha="center", va="center", 
            fontsize=10.5, fontweight="bold", family="serif", color=PURPLE_TC)

    # ========================================================
    # FINAL FORMATTING & SAVE
    # ========================================================
    plt.tight_layout()
    output_path = os.path.join(os.getcwd(), "overall_methodology.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"PNG saved at: {output_path}")

if __name__ == "__main__":
    create_overall_methodology()

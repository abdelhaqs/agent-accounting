"""Generate a visual PNG diagram of the Zerion data pipeline on GCP."""
from __future__ import annotations

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT_PATH = "docs/pipeline_diagram_gcp.png"


def add_box(ax, x: float, y: float, width: float, height: float, text: str, color: str):
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.02",
        facecolor=color,
        edgecolor="#333333",
        linewidth=1.5,
    )
    ax.add_patch(box)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=9,
        weight="bold",
        wrap=True,
    )
    return box


def add_arrow(ax, x1: float, y1: float, x2: float, y2: float, label: str = ""):
    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=15,
        color="#555555",
        linewidth=1.5,
    )
    ax.add_patch(arrow)
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(
            mid_x,
            mid_y + 0.04,
            label,
            ha="center",
            va="bottom",
            fontsize=7,
            style="italic",
            color="#333333",
        )


def main():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Title
    ax.text(
        7.5,
        7.6,
        "Zerion Data Pipeline on GCP",
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
    )

    # Stage labels
    stages = [
        (1.5, "Sources"),
        (4.5, "Ingestion"),
        (7.5, "Warehouse"),
        (10.8, "Transformation"),
        (13.5, "Consumption"),
    ]
    for x, label in stages:
        ax.text(
            x,
            7.1,
            label,
            ha="center",
            va="center",
            fontsize=11,
            weight="bold",
            color="#555555",
        )

    # Boxes
    add_box(ax, 1.5, 5.5, 2.0, 0.7, "Zerion API v1", "#E3F2FD")
    add_box(ax, 4.5, 5.5, 2.2, 0.7, "Cloud Run Job\nPython Sync", "#FFF3E0")
    add_box(ax, 4.5, 6.5, 1.4, 0.5, "Secret Manager", "#FFF9C4")
    add_box(ax, 4.5, 3.8, 2.2, 0.7, "Cloud Storage\nRaw Bucket", "#E8F5E9")
    add_box(ax, 7.5, 4.7, 2.2, 0.7, "BigQuery\nraw_zerion_\ntransactions", "#F3E5F5")
    add_box(ax, 7.5, 3.0, 2.2, 0.7, "BigQuery\nraw_zerion_\npositions", "#F3E5F5")
    add_box(ax, 11.0, 5.5, 2.2, 0.7, "dbt Staging", "#FFEBEE")
    add_box(ax, 11.0, 4.0, 2.2, 0.7, "dbt Intermediate", "#FFEBEE")
    add_box(ax, 11.0, 2.5, 2.2, 0.7, "dbt Marts", "#FFEBEE")
    add_box(ax, 13.5, 5.0, 1.6, 0.7, "Looker\nStudio", "#E0F7FA")
    add_box(ax, 13.5, 3.5, 1.6, 0.7, "Cloud Run\nAPI", "#E0F7FA")
    add_box(ax, 3.5, 1.5, 1.8, 0.6, "Cloud\nScheduler", "#E1F5FE")
    add_box(ax, 5.8, 1.5, 1.8, 0.6, "Cloud\nWorkflows", "#E1F5FE")

    # Arrows
    add_arrow(ax, 2.5, 5.5, 3.4, 5.5, "GET")
    add_arrow(ax, 4.5, 6.25, 4.5, 5.85, "key")
    add_arrow(ax, 4.5, 5.15, 4.5, 4.15, "raw JSON")
    add_arrow(ax, 5.6, 3.8, 6.4, 4.7, "LOAD")
    add_arrow(ax, 5.6, 3.8, 6.4, 3.0, "LOAD")
    add_arrow(ax, 8.6, 4.7, 9.9, 5.5, "load")
    add_arrow(ax, 8.6, 3.0, 9.9, 3.3, "load")
    add_arrow(ax, 11.0, 5.15, 11.0, 4.35, "model")
    add_arrow(ax, 11.0, 3.65, 11.0, 2.85, "model")
    add_arrow(ax, 12.1, 2.5, 12.7, 5.0, "serve")
    add_arrow(ax, 12.1, 2.5, 12.7, 3.5, "serve")
    add_arrow(ax, 4.4, 1.8, 4.4, 5.15, "trigger")
    add_arrow(ax, 5.6, 1.8, 5.6, 5.15, "run")
    add_arrow(ax, 6.7, 1.8, 9.9, 2.15, "orchestrate")

    # Legend
    legend_items = [
        ("#E3F2FD", "Source"),
        ("#FFF3E0", "Compute"),
        ("#E8F5E9", "Object Storage"),
        ("#F3E5F5", "Raw Tables"),
        ("#FFEBEE", "dbt Models"),
        ("#E0F7FA", "Consumers"),
        ("#E1F5FE", "Orchestrator"),
    ]
    for i, (color, label) in enumerate(legend_items):
        rect = mpatches.Rectangle((0.5 + i * 1.9, 0.4), 0.3, 0.3, facecolor=color, edgecolor="#333")
        ax.add_patch(rect)
        ax.text(0.9 + i * 1.9, 0.55, label, va="center", fontsize=8)

    plt.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Diagram saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

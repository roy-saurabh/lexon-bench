"""
Figure generation for LEXON-Bench paper outputs.

Generates:
  outputs/figures/pipeline.png    — 5-stage LEXON pipeline diagram
  outputs/figures/f1_by_task.png  — F1 scores by task and system (bar chart)
  outputs/figures/error_breakdown.png — Error categories for LEXON on test split
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for reproducible rendering

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


SYSTEM_COLORS = {
    "LEXON (full)": "#2c7bb6",
    "B1 Static checklist": "#d7191c",
    "B2 Ontology (no rules)": "#fdae61",
    "B3 Flat rules (no graph)": "#abd9e9",
}


def make_pipeline_figure(output_path: Path) -> None:
    """Generate the 5-stage LEXON pipeline diagram."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stages = [
        ("Stage 1\nLegal text\ndecomposition", "Clause text\n→ Tuples", "#d4e6f1"),
        ("Stage 2\nGraph\npopulation", "Tuples\n→ KG ABox", "#d5e8d4"),
        ("Stage 3\nRule\ncompilation", "TBox+ABox\n→ Datalog", "#fff2cc"),
        ("Stage 4\nInference", "Rules+Facts\n→ Applicable\nGap, Conflict", "#f8cecc"),
        ("Stage 5\nOutput\ngeneration", "Facts\n→ Report\n+ Candidates", "#e1d5e7"),
    ]

    fig, ax = plt.subplots(figsize=(14, 3.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")

    for i, (title, desc, color) in enumerate(stages):
        x = i * 2.8 + 0.1
        box = mpatches.FancyBboxPatch(
            (x, 0.4), 2.4, 3.0,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor="#555",
            linewidth=1.2,
        )
        ax.add_patch(box)
        ax.text(x + 1.2, 2.3, title, ha="center", va="center",
                fontsize=9, fontweight="bold", wrap=True)
        ax.text(x + 1.2, 1.0, desc, ha="center", va="center",
                fontsize=7.5, color="#333")

        if i < len(stages) - 1:
            ax.annotate(
                "", xy=(x + 2.6, 1.9), xytext=(x + 2.4, 1.9),
                arrowprops=dict(arrowstyle="->", color="#555", lw=1.5),
            )

    ax.set_title(
        "LEXON Five-Stage Information Pipeline",
        fontsize=12, fontweight="bold", pad=10,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def make_f1_by_task_figure(
    system_results: dict[str, dict[str, float]],
    output_path: Path,
) -> None:
    """
    Bar chart of F1 scores by task and system.

    system_results: {system_name: {"T1": f1, "T2": f1, "T3": f1}}
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tasks = ["T1 Activation", "T2 Evidence Gaps", "T3 Conflicts"]
    task_keys = ["T1", "T2", "T3"]
    system_names = list(system_results.keys())
    n_systems = len(system_names)
    n_tasks = len(tasks)

    x = np.arange(n_tasks)
    width = 0.8 / n_systems

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, sname in enumerate(system_names):
        vals = [system_results[sname].get(k, 0.0) for k in task_keys]
        color = SYSTEM_COLORS.get(sname, f"C{i}")
        offset = (i - n_systems / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width * 0.9, label=sname, color=color, alpha=0.9)
        for bar, val in zip(bars, vals):
            if val > 0.05:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{val:.2f}",
                    ha="center", va="bottom", fontsize=7.5,
                )

    ax.set_xlabel("Reasoning Task", fontsize=11)
    ax.set_ylabel("F1 Score", fontsize=11)
    ax.set_title("LEXON-Bench F1 by Reasoning Task and System (test split)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.4)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def make_error_breakdown_figure(
    error_counts: dict[str, int],
    output_path: Path,
) -> None:
    """
    Pie / bar chart of LEXON T1 error categories.

    error_counts: {category_label: count}
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    labels = list(error_counts.keys())
    values = [error_counts[k] for k in labels]
    colors = ["#d7191c", "#fdae61", "#2c7bb6", "#1a9641", "#984ea3"][:len(labels)]

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(10)

    ax.legend(
        wedges, [f"{l} ({v})" for l, v in zip(labels, values)],
        title="Error category",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9,
    )
    ax.set_title("LEXON T1 Error Breakdown (test split)", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

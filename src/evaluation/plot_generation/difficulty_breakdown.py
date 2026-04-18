from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from evaluation.plot_generation.constants import DATASETS, PALETTE
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.metrics import aggregates
from evaluation.plot_generation.utils import grouped_bars, rotate_xticks, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def plot_difficulty_across_datasets(
    results: Results,
    difficulty: str,
    output_dir: Path,
) -> None:
    metrics = [
        "parse_success",
        "execution_accuracy",
        "entity_f1",
        "relation_f1",
        "result_f1",
    ]
    labels = ["Parse", "Exec", "Entity", "Relation", "Result"]
    bar_colors = {"SQL": PALETTE["sql"], "Cypher": PALETTE["cypher"]}

    fig, axes = plt.subplots(1, len(DATASETS), figsize=(18, 5))
    for idx, (ax, dataset) in enumerate(zip(axes, DATASETS, strict=True)):
        sql_agg = aggregates(
            collect(results, dataset=dataset, language="sql", difficulty=difficulty),
        )
        cypher_agg = aggregates(
            collect(results, dataset=dataset, language="cypher", difficulty=difficulty),
        )
        grouped_bars(
            ax,
            {
                "SQL": [sql_agg[m] for m in metrics],
                "Cypher": [cypher_agg[m] for m in metrics],
            },
            labels,
            bar_colors,
            0.35,
            "{:.1f}",
            7,
        )
        ax.set_xlabel("Metrics", fontsize=10)
        ax.set_ylabel("Score", fontsize=10)
        ax.set_title(dataset, fontsize=11, fontweight="bold")
        rotate_xticks(ax, 15, 9)
        if idx == 0:
            ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle(
        f"SQL vs Cypher - {difficulty.capitalize()} Queries Across Datasets",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    save(fig, output_dir / f"3_{difficulty}_across_datasets.png")

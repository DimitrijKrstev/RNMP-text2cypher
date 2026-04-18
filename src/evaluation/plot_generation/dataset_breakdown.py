from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from evaluation.plot_generation.constants import DIFFICULTIES, LANGUAGES, PALETTE
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.metrics import aggregates
from evaluation.plot_generation.utils import grouped_bars, rotate_xticks, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def plot_dataset_comparison(results: Results, dataset: str, output_dir: Path) -> None:
    sql_agg = aggregates(
        collect(results, dataset=dataset, language="sql", difficulty=None),
    )
    cypher_agg = aggregates(
        collect(results, dataset=dataset, language="cypher", difficulty=None),
    )

    metrics = [
        "parse_success",
        "execution_accuracy",
        "entity_f1",
        "relation_f1",
        "result_f1",
    ]
    labels = ["Parse", "Exec", "Entity F1", "Relation F1", "Result F1"]

    fig, ax = plt.subplots(figsize=(12, 6))
    grouped_bars(
        ax,
        {
            "SQL": [sql_agg[m] for m in metrics],
            "Cypher": [cypher_agg[m] for m in metrics],
        },
        labels,
        {"SQL": PALETTE["sql"], "Cypher": PALETTE["cypher"]},
        0.35,
        "{:.2f}",
        8,
    )
    ax.set_xlabel("Metrics", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title(
        f"SQL vs Cypher Performance: {dataset}",
        fontsize=14,
        fontweight="bold",
    )
    rotate_xticks(ax, 15, None)
    ax.legend()
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / f"2_{dataset}_sql_vs_cypher.png")


def plot_dataset_difficulty_breakdown(
    results: Results,
    dataset: str,
    output_dir: Path,
) -> None:
    metrics = ["parse_success", "execution_accuracy", "result_f1"]
    labels = ["Parse", "Exec", "Result F1"]
    difficulty_colors = {d.capitalize(): PALETTE[d] for d in DIFFICULTIES}

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax, language in zip(axes, LANGUAGES, strict=True):
        groups = {
            difficulty.capitalize(): [
                aggregates(
                    collect(
                        results,
                        dataset=dataset,
                        language=language,
                        difficulty=difficulty,
                    ),
                )[m]
                for m in metrics
            ]
            for difficulty in DIFFICULTIES
        }
        grouped_bars(ax, groups, labels, difficulty_colors, 0.25, "{:.2f}", 8)
        ax.set_xlabel("Metrics", fontsize=11)
        ax.set_ylabel("Score", fontsize=11)
        ax.set_title(
            f"{language.upper()} - {dataset}",
            fontsize=12,
            fontweight="bold",
        )
        rotate_xticks(ax, 15, None)
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / f"2_{dataset}_difficulty_breakdown.png")

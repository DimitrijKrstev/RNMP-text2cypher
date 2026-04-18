from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from evaluation.plot_generation.constants import (
    DATASETS,
    DIFFICULTIES,
    LANGUAGES,
    PALETTE,
)
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.metrics import mean_attr, rate
from evaluation.plot_generation.utils import heatmap, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def plot_execution_accuracy_heatmap(results: Results, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, language in zip(axes, LANGUAGES, strict=True):
        data = np.array(
            [
                [
                    rate(
                        collect(
                            results,
                            dataset=ds,
                            language=language,
                            difficulty=d,
                        ),
                        lambda r: r.execution_accuracy,
                    )
                    for d in DIFFICULTIES
                ]
                for ds in DATASETS
            ],
        )
        heatmap(
            ax,
            fig,
            data,
            list(DATASETS),
            [d.capitalize() for d in DIFFICULTIES],
            "RdYlGn",
            0.0,
            1.0,
            "{:.2f}",
        )
        ax.set_xlabel("Difficulty", fontsize=11)
        ax.set_ylabel("Dataset", fontsize=11)
        ax.set_title(
            f"{language.upper()} Execution Accuracy",
            fontsize=12,
            fontweight="bold",
        )
    save(fig, output_dir / "5_execution_accuracy_heatmap.png")


def plot_precision_recall(results: Results, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    for language in LANGUAGES:
        bucket = collect(results, dataset=None, language=language, difficulty=None)
        ax.scatter(
            [r.result_recall for r in bucket],
            [r.result_precision for r in bucket],
            alpha=0.5,
            s=30,
            color=PALETTE[language],
            label=language.capitalize(),
            edgecolors="black",
            linewidth=0.5,
        )
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Perfect P=R")
    ax.set_xlabel("Recall", fontsize=12)
    ax.set_ylabel("Precision", fontsize=12)
    ax.set_title("Precision vs Recall Distribution", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)

    ax = axes[1]
    x = np.arange(len(DIFFICULTIES))
    width = 0.2
    series = [
        ("SQL Precision", "sql", "result_precision", 0.8),
        ("SQL Recall", "sql", "result_recall", 0.5),
        ("Cypher Precision", "cypher", "result_precision", 0.8),
        ("Cypher Recall", "cypher", "result_recall", 0.5),
    ]
    for i, (label, lang, attr, alpha) in enumerate(series):
        values = [
            mean_attr(
                collect(results, dataset=None, language=lang, difficulty=d),
                attr,
            )
            for d in DIFFICULTIES
        ]
        ax.bar(
            x + (i - 1.5) * width,
            values,
            width,
            label=label,
            color=PALETTE[lang],
            alpha=alpha,
        )
    ax.set_xlabel("Difficulty", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Precision & Recall by Difficulty", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in DIFFICULTIES])
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / "5_precision_recall.png")

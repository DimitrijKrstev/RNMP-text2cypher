from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from evaluation.plot_generation.constants import (
    DATASETS,
    DIFFICULTIES,
    LANGUAGES,
    PALETTE,
    STRUCTURAL_COMPONENTS,
)
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.metrics import mean_attr
from evaluation.plot_generation.utils import annotate_bars, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def plot_structural_component(
    results: Results,
    component: str,
    label: str,
    output_dir: Path,
) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f"{label} Performance", fontsize=16, fontweight="bold")

    for row, language in enumerate(LANGUAGES):
        for col, dataset in enumerate(DATASETS):
            ax = axes[row, col]
            values = [
                mean_attr(
                    collect(
                        results,
                        dataset=dataset,
                        language=language,
                        difficulty=d,
                    ),
                    component,
                )
                for d in DIFFICULTIES
            ]
            bars = ax.bar(
                list(DIFFICULTIES),
                values,
                color=PALETTE[language],
                alpha=0.8,
            )
            annotate_bars(ax, bars, "{:.2f}", 9)
            ax.set_title(
                f"{language.upper()} - {dataset}",
                fontsize=11,
                fontweight="bold",
            )
            ax.set_ylabel("F1 Score", fontsize=10)
            if row == 1:
                ax.set_xlabel("Difficulty", fontsize=10)
            ax.set_ylim(0, 1.0)
            ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / f"4_{component}.png")


def plot_structural_radar(results: Results, output_dir: Path) -> None:
    comps = [c for c, _ in STRUCTURAL_COMPONENTS]
    labels = [name for _, name in STRUCTURAL_COMPONENTS]

    n = len(labels)
    angles = [i / n * 2 * pi for i in range(n)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": "polar"})
    for language in LANGUAGES:
        bucket = collect(results, dataset=None, language=language, difficulty=None)
        values = [mean_attr(bucket, c) for c in comps]
        closed = [*values, values[0]]
        color = PALETTE[language]
        ax.plot(
            angles,
            closed,
            "o-",
            linewidth=2,
            label=language.capitalize(),
            color=color,
        )
        ax.fill(angles, closed, alpha=0.25, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=9)
    ax.grid(visible=True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=12)
    ax.set_title(
        "Structural Components Comparison\n(SQL vs Cypher)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    save(fig, output_dir / "4_structural_radar.png")

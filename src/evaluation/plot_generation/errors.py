from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from evaluation.plot_generation.constants import DATASETS, DIFFICULTIES, LANGUAGES
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.latex import write_latex_table
from evaluation.plot_generation.metrics import all_error_categories, error_counts
from evaluation.plot_generation.utils import heatmap, rotate_xticks, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def _percentages(
    counts: dict[str, int], total: int, categories: list[str]
) -> list[float]:
    return [(counts.get(c, 0) / total * 100) if total else 0.0 for c in categories]


def plot_error_distribution(results: Results, output_dir: Path) -> None:
    sql_counts, total_sql = error_counts(
        collect(results, dataset=None, language="sql", difficulty=None),
    )
    cypher_counts, total_cypher = error_counts(
        collect(results, dataset=None, language="cypher", difficulty=None),
    )
    categories = sorted(set(sql_counts) | set(cypher_counts))

    if not categories:
        print("No errors found to plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(categories)))
    for ax, language, percentages in [
        (axes[0], "sql", _percentages(sql_counts, total_sql, categories)),
        (axes[1], "cypher", _percentages(cypher_counts, total_cypher, categories)),
    ]:
        _, _, autotexts = ax.pie(
            percentages,
            labels=categories,
            autopct="%1.1f%%",
            colors=colors_pie,
            startangle=90,
        )
        ax.set_title(
            f"{language.upper()} Error Distribution",
            fontsize=13,
            fontweight="bold",
        )
        for t in autotexts:
            t.set_color("black")
            t.set_fontsize(9)
    save(fig, output_dir / "6_error_distribution.png")

    rows = []
    for category in categories:
        sc = sql_counts.get(category, 0)
        cc = cypher_counts.get(category, 0)
        sp = (sc / total_sql * 100) if total_sql else 0.0
        cp = (cc / total_cypher * 100) if total_cypher else 0.0
        rows.append(
            [
                category.replace("_", " ").title(),
                str(sc),
                f"{sp:.1f}\\%",
                str(cc),
                f"{cp:.1f}\\%",
            ],
        )
    write_latex_table(
        output_dir / "6_error_table.tex",
        "Error Category Distribution",
        ["Error Category", "SQL Count", "SQL \\%", "Cypher Count", "Cypher \\%"],
        rows,
        "",
    )


def plot_error_by_dataset_heatmap(results: Results, output_dir: Path) -> None:
    categories = all_error_categories(results)
    if not categories:
        print("No errors found for heatmap")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, language in zip(axes, LANGUAGES, strict=True):
        data = np.zeros((len(DATASETS), len(categories)))
        for i, dataset in enumerate(DATASETS):
            counts, total = error_counts(
                collect(results, dataset=dataset, language=language, difficulty=None),
            )
            for j, cat in enumerate(categories):
                data[i, j] = (counts.get(cat, 0) / total * 100) if total else 0.0

        heatmap(
            ax,
            fig,
            data,
            list(DATASETS),
            [c.replace("_", "\n") for c in categories],
            "YlOrRd",
            0.0,
            50.0,
            "{:.1f}",
        )
        rotate_xticks(ax, 45, 9)
        ax.set_xlabel("Error Category", fontsize=11)
        ax.set_ylabel("Dataset", fontsize=11)
        ax.set_title(
            f"{language.upper()} Error Distribution by Dataset (%)",
            fontsize=12,
            fontweight="bold",
        )
    save(fig, output_dir / "6_error_by_dataset_heatmap.png")


def plot_error_by_difficulty(results: Results, output_dir: Path) -> None:
    categories = all_error_categories(results)
    if not categories:
        print("No errors found for difficulty plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, language in zip(axes, LANGUAGES, strict=True):
        per_cat: dict[str, list[float]] = {c: [] for c in categories}
        for difficulty in DIFFICULTIES:
            counts, total = error_counts(
                collect(
                    results,
                    dataset=None,
                    language=language,
                    difficulty=difficulty,
                ),
            )
            for c in categories:
                per_cat[c].append((counts.get(c, 0) / total * 100) if total else 0.0)

        x = np.arange(len(DIFFICULTIES))
        width = 0.8 / len(categories)
        for i, (cat, values) in enumerate(per_cat.items()):
            offset = (i - len(categories) / 2) * width + width / 2
            ax.bar(x + offset, values, width, label=cat.replace("_", " ").title())

        ax.set_xlabel("Difficulty", fontsize=12)
        ax.set_ylabel("Error Rate (%)", fontsize=12)
        ax.set_title(
            f"{language.upper()} Errors by Difficulty",
            fontsize=13,
            fontweight="bold",
        )
        ax.set_xticks(x)
        ax.set_xticklabels([d.capitalize() for d in DIFFICULTIES])
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / "6_error_by_difficulty.png")

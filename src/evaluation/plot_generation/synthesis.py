from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from evaluation.plot_generation.constants import (
    DATASETS,
    DIFFICULTIES,
    LANGUAGES,
    PALETTE,
    SYNTHESIS_METRICS,
)
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.latex import write_latex_table
from evaluation.plot_generation.metrics import aggregates, rate
from evaluation.plot_generation.utils import save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


def plot_parse_success_comparison(results: Results, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(DATASETS))
    width = 0.15

    for i, difficulty in enumerate(DIFFICULTIES):
        for lang_idx, language in enumerate(LANGUAGES):
            rates = [
                rate(
                    collect(
                        results,
                        dataset=ds,
                        language=language,
                        difficulty=difficulty,
                    ),
                    lambda r: r.parse_success,
                )
                for ds in DATASETS
            ]
            offset = (i - 1.5 + lang_idx * 0.5) * width
            ax.bar(
                x + offset,
                rates,
                width,
                label=f"{language.capitalize()} {difficulty.capitalize()}",
                color=PALETTE[language],
                alpha=0.4 + i * 0.2,
            )

    ax.set_xlabel("Dataset", fontsize=12)
    ax.set_ylabel("Parse Success Rate", fontsize=12)
    ax.set_title(
        "Parse Success Comparison (SQL vs Cypher)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(list(DATASETS))
    ax.legend(ncol=2, fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / "7_parse_success_comparison.png")


def _winner(sv: float, cv: float) -> str:
    if abs(sv - cv) < 0.01:
        return "Tie"
    return "SQL" if sv > cv else "Cypher"


def plot_final_synthesis(results: Results, output_dir: Path) -> None:
    sql_agg = aggregates(
        collect(results, dataset=None, language="sql", difficulty=None)
    )
    cypher_agg = aggregates(
        collect(results, dataset=None, language="cypher", difficulty=None),
    )

    wins = {"sql": 0, "cypher": 0, "tie": 0}
    for m in SYNTHESIS_METRICS:
        sv, cv = sql_agg[m], cypher_agg[m]
        if abs(sv - cv) < 0.01:
            wins["tie"] += 1
        elif sv > cv:
            wins["sql"] += 1
        else:
            wins["cypher"] += 1

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    ax.pie(
        [wins["sql"], wins["cypher"], wins["tie"]],
        labels=["SQL Wins", "Cypher Wins", "Ties"],
        autopct="%1.0f%%",
        colors=[PALETTE["sql"], PALETTE["cypher"], PALETTE["tie"]],
        startangle=90,
    )
    ax.set_title(
        "Overall Performance Comparison\n(SQL vs Cypher Wins by Metric)",
        fontsize=13,
        fontweight="bold",
    )

    ax = axes[1]
    x = np.arange(len(SYNTHESIS_METRICS))
    width = 0.35
    sql_vals = [sql_agg[m] for m in SYNTHESIS_METRICS]
    cypher_vals = [cypher_agg[m] for m in SYNTHESIS_METRICS]
    for offset, values, label, color in [
        (-width / 2, sql_vals, "SQL", PALETTE["sql"]),
        (width / 2, cypher_vals, "Cypher", PALETTE["cypher"]),
    ]:
        bars = ax.barh(x + offset, values, width, label=label, color=color)
        for bar in bars:
            w = bar.get_width()
            ax.text(
                w,
                bar.get_y() + bar.get_height() / 2.0,
                f"{w:.2f}",
                ha="left",
                va="center",
                fontsize=8,
            )
    ax.set_yticks(x)
    ax.set_yticklabels(
        [m.replace("_", " ").title() for m in SYNTHESIS_METRICS],
        fontsize=9,
    )
    ax.set_xlabel("Score", fontsize=12)
    ax.set_title("Metric-by-Metric Comparison", fontsize=13, fontweight="bold")
    ax.legend()
    ax.set_xlim(0, 1.0)
    ax.grid(axis="x", alpha=0.3)
    save(fig, output_dir / "7_final_synthesis.png")

    rows = [
        [
            m.replace("_", " ").title(),
            f"{sql_agg[m]:.3f}",
            f"{cypher_agg[m]:.3f}",
            _winner(sql_agg[m], cypher_agg[m]),
        ]
        for m in SYNTHESIS_METRICS
    ]
    summary = (
        "\\hline\n"
        "\\multicolumn{4}{l}{\\textbf{Summary:}} \\\\\n"
        f"SQL Wins & \\multicolumn{{3}}{{l}}{{{wins['sql']}}} \\\\\n"
        f"Cypher Wins & \\multicolumn{{3}}{{l}}{{{wins['cypher']}}} \\\\\n"
        f"Ties & \\multicolumn{{3}}{{l}}{{{wins['tie']}}} \\\\\n"
    )
    write_latex_table(
        output_dir / "7_synthesis_table.tex",
        "SQL vs Cypher Performance Synthesis",
        ["Metric", "SQL", "Cypher", "Winner"],
        rows,
        summary,
    )

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from evaluation.plot_generation.constants import PALETTE
from evaluation.plot_generation.data import collect
from evaluation.plot_generation.latex import write_latex_table
from evaluation.plot_generation.metrics import aggregates
from evaluation.plot_generation.utils import grouped_bars, save

if TYPE_CHECKING:
    from pathlib import Path

    from evaluation.plot_generation.data import Results


_OVERALL_ROWS: tuple[tuple[str, str], ...] = (
    ("Parse Success", "parse_success"),
    ("Execution Accuracy", "execution_accuracy"),
    ("Correct Result", "correct_result"),
    ("Result F1", "result_f1"),
    ("Entity F1", "entity_f1"),
    ("Attribute F1", "attribute_f1"),
    ("Relation F1", "relation_f1"),
    ("Filter F1", "filter_f1"),
    ("Aggregation F1", "aggregation_f1"),
    ("Return Column F1", "return_column_f1"),
)


def plot_overall(results: Results, output_dir: Path) -> None:
    sql_agg = aggregates(
        collect(results, dataset=None, language="sql", difficulty=None)
    )
    cypher_agg = aggregates(
        collect(results, dataset=None, language="cypher", difficulty=None),
    )

    metrics = ["parse_success", "correct_result", "result_f1"]
    labels = ["Parse Success", "Executable", "Result F1"]

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
        9,
    )
    ax.set_xlabel("Metrics", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Overall SQL vs Cypher Performance", fontsize=14, fontweight="bold")
    ax.legend()
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)
    save(fig, output_dir / "1_overall_sql_vs_cypher.png")

    write_latex_table(
        output_dir / "1_overall_table.tex",
        "Overall SQL vs Cypher Performance",
        ["Metric", "SQL", "Cypher"],
        [
            [label, f"{sql_agg[k]:.3f}", f"{cypher_agg[k]:.3f}"]
            for label, k in _OVERALL_ROWS
        ],
        "",
    )

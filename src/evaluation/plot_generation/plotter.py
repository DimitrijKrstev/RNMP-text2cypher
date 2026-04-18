from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from evaluation.plot_generation.accuracy import (
    plot_execution_accuracy_heatmap,
    plot_precision_recall,
)
from evaluation.plot_generation.constants import (
    DATASETS,
    DIFFICULTIES,
    MPL_STYLE,
    STRUCTURAL_COMPONENTS,
)
from evaluation.plot_generation.data import load_results
from evaluation.plot_generation.dataset_breakdown import (
    plot_dataset_comparison,
    plot_dataset_difficulty_breakdown,
)
from evaluation.plot_generation.difficulty_breakdown import (
    plot_difficulty_across_datasets,
)
from evaluation.plot_generation.errors import (
    plot_error_by_dataset_heatmap,
    plot_error_by_difficulty,
    plot_error_distribution,
)
from evaluation.plot_generation.overall import plot_overall
from evaluation.plot_generation.structural import (
    plot_structural_component,
    plot_structural_radar,
)
from evaluation.plot_generation.synthesis import (
    plot_final_synthesis,
    plot_parse_success_comparison,
)

if TYPE_CHECKING:
    from pathlib import Path


def generate_all_plots(results_dir: Path, output_dir: Path, model: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use(MPL_STYLE)

    print("Loading all results...")
    results = load_results(results_dir, model)

    print("\nSection 1: Aggregate Results")
    plot_overall(results, output_dir)

    print("\nSection 2: Results by Dataset")
    for dataset in DATASETS:
        print(f"  Processing {dataset}...")
        plot_dataset_comparison(results, dataset, output_dir)
        plot_dataset_difficulty_breakdown(results, dataset, output_dir)

    print("\nSection 3: Results by Difficulty")
    for difficulty in DIFFICULTIES:
        print(f"  Processing {difficulty}...")
        plot_difficulty_across_datasets(results, difficulty, output_dir)

    print("\nSection 4: Structural Analysis")
    for comp, label in STRUCTURAL_COMPONENTS:
        print(f"  Processing {label}...")
        plot_structural_component(results, comp, label, output_dir)
    print("  Generating radar chart...")
    plot_structural_radar(results, output_dir)

    print("\nSection 5: Result Accuracy")
    plot_execution_accuracy_heatmap(results, output_dir)
    plot_precision_recall(results, output_dir)

    print("\nSection 6: Error Analysis")
    plot_error_distribution(results, output_dir)
    plot_error_by_dataset_heatmap(results, output_dir)
    plot_error_by_difficulty(results, output_dir)

    print("\nSection 7: Comparative Synthesis")
    plot_parse_success_comparison(results, output_dir)
    plot_final_synthesis(results, output_dir)

    print(f"\nAll outputs saved to: {output_dir}")

from pathlib import Path

from models import TaskResult, TaskType
import json
from collections import Counter
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def plot_results(dataset_name: str) -> None:
    results_dir = PROJECT_ROOT / "results" / dataset_name

    for task_type in results_dir.iterdir():
        if not task_type.is_dir():
            continue
        plot_for_task_type(task_type, dataset_name)


def plot_for_task_type(task_type: Path, dataset_name: str) -> None:
    for model_name in task_type.iterdir():
        if not model_name.is_dir():
            continue
        plot_for_model(
            model_name, 
            TaskType.SQL if task_type.name == "sql" else TaskType.CYPHER,
            dataset_name
        )


def plot_for_model(model_name: Path, task_type: TaskType, dataset_name: str) -> None:
    for result_json in model_name.glob("*.json"):
        plot_for_result_json(result_json, task_type, model_name.name, dataset_name)


def plot_for_result_json(
    result_json: Path,
    task_type: TaskType,
    model_name: str,
    dataset_name: str,
) -> None:
    results = [
        TaskResult.from_dict(r, task_type) for r in json.load(result_json.open())
    ]

    fields = ["syntaxically_correct", "correct_result", "exact_match"]
    counts = Counter(
        {
            field: sum(getattr(result, field, False) for result in results)
            for field in fields
        }
    )

    plt.figure(figsize=(10, 8))
    bars = plt.bar(fields, [counts[field] for field in fields])

    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            int(yval),
            ha="center",
            va="bottom",
        )
    plt.xlabel(f"Metrics for {result_json.stem}")
    plt.ylabel("Number of True Results")
    plt.title(f"{model_name} - {task_type.name}")
    plt.tight_layout()

    plots_dir = PROJECT_ROOT / "plots" / dataset_name
    plots_dir.mkdir(parents=True, exist_ok=True)
    plot_filename = f"{model_name}_{task_type.name}_{result_json.stem}.png"
    plt.savefig(plots_dir / plot_filename)
    plt.close()
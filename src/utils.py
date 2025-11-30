import json
import os
from pathlib import Path
from typing import Any, Tuple
from constants import RESULTS_DIR
from models import Task, TaskDifficulty, TaskResult, TaskType


def get_tasks_from_json(path: Path) -> list[Task]:
    return [Task.from_dict(line) for line in json.load(open(path, "r"))]


def save_task_results(
    task_results: list[TaskResult],
    dataset_name: str,
    task_difficulty: TaskDifficulty,
    task_type: TaskType,
    model_name: str,
) -> None:
    result_dicts = [task_result.to_dict() for task_result in task_results]

    model_name_slug = model_name.replace("/", "_")
    result_dir = (
        RESULTS_DIR
        / dataset_name
        / task_type.value.lower()
        / model_name_slug
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    file_path = result_dir / f"{task_difficulty.value}.json"

    try:
        with open(file_path, "w") as json_file:
            json.dump(result_dicts, json_file, indent=2)
            json_file.write("\n")
        print(f"Saved results to {file_path}")

    except Exception as e:
        print(f"Error saving results: {e}")





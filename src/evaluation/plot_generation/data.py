from __future__ import annotations

import json
from collections import defaultdict
from typing import TYPE_CHECKING

from evaluation.plot_generation.constants import (
    DATASETS,
    DIFFICULTIES,
    LANGUAGE_TASK_TYPE,
    LANGUAGES,
)
from models import TaskResult

if TYPE_CHECKING:
    from pathlib import Path

Results = dict[str, dict[str, dict[str, list[TaskResult]]]]


def load_results(results_dir: Path, model: str) -> Results:
    out: Results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for dataset in DATASETS:
        for language in LANGUAGES:
            task_type = LANGUAGE_TASK_TYPE[language]
            for difficulty in DIFFICULTIES:
                path = results_dir / dataset / language / model / f"{difficulty}.json"
                if not path.exists():
                    continue
                with path.open() as f:
                    data = json.load(f)
                out[dataset][language][difficulty] = [
                    TaskResult.from_dict(item, task_type) for item in data
                ]
    return out


def collect(
    results: Results,
    *,
    dataset: str | None,
    language: str | None,
    difficulty: str | None,
) -> list[TaskResult]:
    datasets = (dataset,) if dataset else DATASETS
    languages = (language,) if language else LANGUAGES
    difficulties = (difficulty,) if difficulty else DIFFICULTIES
    out: list[TaskResult] = []
    for ds in datasets:
        for lang in languages:
            for diff in difficulties:
                out.extend(results[ds][lang].get(diff, []))
    return out

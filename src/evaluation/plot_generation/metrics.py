from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np

from evaluation.plot_generation.constants import NON_ERROR_CATEGORIES
from evaluation.plot_generation.data import collect

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from evaluation.plot_generation.data import Results
    from models import TaskResult


def rate(
    results: Iterable[TaskResult],
    predicate: Callable[[TaskResult], bool],
) -> float:
    items = list(results)
    return sum(1 for r in items if predicate(r)) / len(items) if items else 0.0


def mean_attr(results: Iterable[TaskResult], attr: str) -> float:
    values = [v for r in results if (v := getattr(r, attr)) is not None]
    return float(np.mean(values)) if values else 0.0


def aggregates(results: list[TaskResult]) -> dict[str, float]:
    return {
        "parse_success": rate(results, lambda r: r.parse_success),
        "execution_accuracy": rate(results, lambda r: r.execution_accuracy),
        "correct_result": rate(results, lambda r: r.execution_success),
        "entity_f1": mean_attr(results, "entity_f1"),
        "attribute_f1": mean_attr(results, "attribute_f1"),
        "relation_f1": mean_attr(results, "relation_f1"),
        "filter_f1": mean_attr(results, "filter_f1"),
        "aggregation_f1": mean_attr(results, "aggregation_f1"),
        "return_column_f1": mean_attr(results, "return_column_f1"),
        "result_f1": mean_attr(results, "result_f1"),
        "result_precision": mean_attr(results, "result_precision"),
        "result_recall": mean_attr(results, "result_recall"),
    }


def error_counts(results: Iterable[TaskResult]) -> tuple[dict[str, int], int]:
    counts: dict[str, int] = defaultdict(int)
    total = 0
    for r in results:
        total += 1
        if r.error_category not in NON_ERROR_CATEGORIES:
            counts[r.error_category] += 1
    return dict(counts), total


def all_error_categories(results: Results) -> list[str]:
    cats: set[str] = set()
    for r in collect(results, dataset=None, language=None, difficulty=None):
        if r.error_category not in NON_ERROR_CATEGORIES:
            cats.add(r.error_category)
    return sorted(cats)

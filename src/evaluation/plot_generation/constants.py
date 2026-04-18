from __future__ import annotations

from models import TaskType

DATASETS: tuple[str, ...] = ("rel-f1", "rel-stack", "rel-trial")
DIFFICULTIES: tuple[str, ...] = ("easy", "intermediate", "hard")
LANGUAGES: tuple[str, ...] = ("sql", "cypher")

LANGUAGE_TASK_TYPE = {"sql": TaskType.SQL, "cypher": TaskType.CYPHER}

NON_ERROR_CATEGORIES = frozenset({"NONE", "CORRECT"})

PALETTE = {
    "sql": "#2E86AB",
    "cypher": "#A23B72",
    "easy": "#06A77D",
    "intermediate": "#F18F01",
    "hard": "#C73E1D",
    "tie": "#888888",
}

STRUCTURAL_COMPONENTS: tuple[tuple[str, str], ...] = (
    ("entity_f1", "Entity F1"),
    ("attribute_f1", "Attribute F1"),
    ("relation_f1", "Relation F1"),
    ("filter_f1", "Filter F1"),
    ("aggregation_f1", "Aggregation F1"),
    ("return_column_f1", "Return Column F1"),
)

SYNTHESIS_METRICS: tuple[str, ...] = (
    "parse_success",
    "execution_accuracy",
    "entity_f1",
    "attribute_f1",
    "relation_f1",
    "filter_f1",
    "aggregation_f1",
    "return_column_f1",
    "result_f1",
)

MPL_STYLE = "seaborn-v0_8-darkgrid"
DPI = 300

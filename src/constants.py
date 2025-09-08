from pathlib import Path

PRETRAINED_SQL_MODEL_NAME = "defog/sqlcoder-7b-2"
BASE_MODEL_NAME = "google/gemma-3-4b-it"

TASKS_DIRECTORY = Path(__file__).parent / "tasks"
RESULTS_DIRECTORY = Path(__file__).parent.parent / "results"

from pathlib import Path

PRETRAINED_SQL_MODEL_NAME = "defog/sqlcoder-7b-2"
BASE_MODEL_NAME = "meta-llama/Llama-3.1-8B"
REMOTE_MODEL_NAME = "gpt-5-nano"

TASKS_DIRECTORY = Path(__file__).parent / "tasks"
RESULTS_DIRECTORY = Path(__file__).parent.parent / "results"

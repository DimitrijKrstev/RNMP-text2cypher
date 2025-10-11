from pathlib import Path

PRETRAINED_SQL_MODEL_NAME = "defog/sqlcoder-7b-2"
BASE_MODEL_NAME = "meta-llama/Llama-3.1-8B"
REMOTE_MODEL_NAME = "gpt-5-nano"

BASE_DIR = Path(__file__).parent
TASKS_DIRECTORY = BASE_DIR / "tasks"
RESULTS_DIRECTORY = BASE_DIR / "results"

SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

TASKS_DIR = SRC_DIR / "tasks"
RESULTS_DIR = SRC_DIR / "results"
SQLITE_DIR = PROJECT_ROOT / "sqlite"
CSV_OUTPUT_DIR = PROJECT_ROOT / "neo4j" / "import"


def get_tasks_directory(dataset_name: str) -> Path:
    return TASKS_DIR / dataset_name


def get_sqlite_db_path(dataset_name: str) -> Path:
    return SQLITE_DIR / f"{dataset_name}.db"


def get_csv_output_dir(dataset_name: str) -> Path:
    csv_dir = CSV_OUTPUT_DIR / dataset_name
    csv_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir

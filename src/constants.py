from pathlib import Path

from models import DatasetName

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


def get_tasks_directory(dataset_name: DatasetName) -> Path:
    return TASKS_DIR / dataset_name


def get_sqlite_db_path(dataset_name: DatasetName) -> Path:
    print(SQLITE_DIR / dataset_name.value / "relbench.db")
    return SQLITE_DIR / dataset_name.value / "relbench.db"


def get_csv_output_dir(dataset_name: DatasetName) -> Path:
    csv_dir = CSV_OUTPUT_DIR / dataset_name
    csv_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir

from litellm import completion
import os
from logging import getLogger
from constants import get_duckdb_path, get_tasks_directory
from database.neo4j import get_neo4j_schema
from database.duckdb import get_duckdb_schema
from models import DatasetName, TaskDifficulty, TaskType
from utils import get_tasks_from_json, save_task_results
from evaluation.remote_eval_utils import process_tasks

logger = getLogger(__name__)

schema_generator = {
    TaskType.SQL: get_duckdb_schema,
    TaskType.CYPHER: get_neo4j_schema,
}

db_path_resolver = {
    TaskType.SQL: get_duckdb_path,
    TaskType.CYPHER: lambda _: None,
}

def evaluate_remote_model(
    model_name: str,
    dataset_name: DatasetName,
    task_type: TaskType,
    api_key: str | None = None,
) -> None:
    """Evaluate a remote model on a dataset."""
    schema = schema_generator[task_type]()
    db_path = db_path_resolver[task_type](dataset_name)
    tasks_dir = get_tasks_directory(dataset_name)

    for difficulty in TaskDifficulty:
        tasks_file = tasks_dir / f"{difficulty.value}.json"

        if not tasks_file.exists():
            logger.warning(f"Skipping missing: {tasks_file}")
            continue

        tasks = get_tasks_from_json(tasks_file)
        logger.info(f"Processing {len(tasks)} tasks for {difficulty.value}")

        results = process_tasks(tasks, task_type, schema, db_path, model_name, api_key)

        save_task_results(results, dataset_name, difficulty, task_type, model_name)
        logger.info(f"Completed {difficulty.value}: {len(results)} results")
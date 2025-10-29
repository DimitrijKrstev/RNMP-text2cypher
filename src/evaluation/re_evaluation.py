from logging import getLogger
import json
from tqdm import tqdm

from constants import REMOTE_MODEL_NAME, get_sqlite_db_path, RESULTS_DIR, get_duckdb_path
from database.neo4j import get_neo4j_schema
from evaluation.scoring import get_task_result
from models import DatasetName, TaskDifficulty, TaskType, Task, TaskResult
from utils import save_task_results

logger = getLogger(__name__)

def re_evaluate_sql_results(dataset_name: DatasetName) -> None:
    """Re-evaluate SQL results for a given already_generated dataset"""

    # db_path = get_sqlite_db_path(dataset_name)
    # Should be duckdb for now
    # TODO: Make this dynamic based on sql/db type used
    db_path = get_duckdb_path(dataset_name)

    for task_difficulty in TaskDifficulty:
        result_file = RESULTS_DIR / dataset_name / "sql" / "gpt-5-nano" / f"{task_difficulty.value}.json"
        if not result_file.exists():
            logger.warning(f"Result file not found, skipping: {result_file}")
            continue

        with open(result_file, 'r') as f:
            existing_results = json.load(f)
        
        task_results = []
        
        for result_data in tqdm(
            existing_results, 
            desc=f"Re-evaluating SQL Tasks ({dataset_name}, {task_difficulty})"
        ):
            task = Task(
                question=result_data["question"],
                sql=result_data["expected_script"],
                cypher="",
                cypher_result=None
            )
            
            generated_query = result_data["generated_script"]
            
            try:
                result = get_task_result(task, generated_query, TaskType.SQL, db_path)
            except Exception as e:
                logger.error(f"Error on query: {generated_query[:100]}... Error: {e}")
                result = TaskResult(
                    task=task,
                    response=generated_query,
                    syntaxically_correct=False,
                    correct_result=False,
                    exact_match=False,
                    task_type=TaskType.SQL
                )

            task_results.append(result)
        
        save_task_results(
            task_results, 
            dataset_name, 
            task_difficulty, 
            TaskType.SQL, 
            REMOTE_MODEL_NAME
        )
        
        logger.info(f"Re-evaluated {len(task_results)} SQL tasks for {task_difficulty}")
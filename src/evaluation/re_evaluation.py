from logging import getLogger
import json
from tqdm import tqdm

from constants import REMOTE_MODEL_NAME, get_sqlite_db_path, RESULTS_DIR, get_duckdb_path
from database.neo4j import get_neo4j_schema
from evaluation.scoring import get_task_result
from models import DatasetName, TaskDifficulty, TaskType, Task, TaskResult
from utils import save_task_results

logger = getLogger(__name__)

def re_evaluate_results(dataset_name: DatasetName, task_type: TaskType) -> None:
    """Re-evaluate SQL or Cypher results for a given already_generated dataset"""

    if task_type == TaskType.SQL:
        db_path = get_duckdb_path(dataset_name)
    else:  
        db_path = None

    for task_difficulty in TaskDifficulty:
        result_file = RESULTS_DIR / dataset_name / task_type.value.lower() / "gpt-5-nano" / f"{task_difficulty.value}.json"
        if not result_file.exists():
            logger.warning(f"Result file not found, skipping: {result_file}")
            continue

        with open(result_file, 'r') as f:
            existing_results = json.load(f)
        
        task_results = []
        
        for result_data in tqdm(
            existing_results, 
            desc=f"Re-evaluating {task_type.value} Tasks ({dataset_name}, {task_difficulty})"
        ):
            if task_type == TaskType.SQL:
                task = Task(
                    question=result_data["question"],
                    sql=result_data["expected_script"],
                    cypher="",
                    cypher_result=None
                )
            else:  
                task = Task(
                    question=result_data["question"],
                    sql="",
                    cypher=result_data["expected_script"],
                    cypher_result=None  
                )
            
            generated_query = result_data["generated_script"]
            
            try:
                result = get_task_result(task, generated_query, task_type, db_path)
            except Exception as e:
                logger.error(f"Error on query: {generated_query[:100]}... Error: {e}")
                result = TaskResult(
                    task=task,
                    response=generated_query,
                    syntaxically_correct=False,
                    correct_result=False,
                    exact_match=False,
                    task_type=task_type
                )

            task_results.append(result)
        
        save_task_results(
            task_results, 
            dataset_name, 
            task_difficulty, 
            task_type, 
            REMOTE_MODEL_NAME
        )
        
        logger.info(f"Re-evaluated {len(task_results)} {task_type.value} tasks for {task_difficulty}")
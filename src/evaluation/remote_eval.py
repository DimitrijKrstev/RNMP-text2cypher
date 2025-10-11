from logging import getLogger

from openai import OpenAI
from tqdm import tqdm

from constants import REMOTE_MODEL_NAME, get_sqlite_db_path, get_tasks_directory
from database.neo4j import get_neo4j_schema
from database.sqlite import get_sqlite_tables
from evaluation.scoring import get_task_result
from models import TaskDifficulty, TaskType
from utils import build_remote_prompt, get_tasks_from_json, save_task_results

logger = getLogger(__name__)


def evaluate_remote_model_for_task(
    dataset_name: str, model_name: str, task_type: TaskType, client: OpenAI
) -> None:
    """Evaluate a remote model for a given dataset and task type"""
    client = OpenAI()
    model_name = REMOTE_MODEL_NAME

    if task_type == TaskType.SQL:
        db_path = get_sqlite_db_path(dataset_name)
        schema = get_sqlite_tables(db_path)
    else:
        schema = get_neo4j_schema(dataset_name) 

    tasks_dir = get_tasks_directory(dataset_name)

    for task_difficulty in TaskDifficulty:
        tasks_file = tasks_dir / f"{task_difficulty.value}.json"
        if not tasks_file.exists():
            logger.warning(f"Tasks file not found, skipping: {tasks_file}")
            continue

        tasks = get_tasks_from_json(tasks_file)
        task_results = []

        for task in tqdm(tasks, f"Tasks ({dataset_name}, {task_difficulty}, {task_type})"):
            prompt = build_remote_prompt(task_type, task.question, schema)

            response = client.responses.create(
                model="gpt-5",
                reasoning={"effort": "low"},
                instructions=(
                    f"You are a Text-to-{task_type} assistant. Return ONLY a raw valid {task_type} statement."
                    "No explanations, no comments, no code fences.\n"
                    "Do NOT order results unless explicitly asked.\n"
                    "Do NOT use column or table aliases unless explicitly asked.\n"
                    "Do NOT use 'AS' for aggregate functions like COUNT, SUM, AVG, etc. unless explicitly asked\n"
                    "Do NOT return DISTINCT values unless explicitly asked.\n"
                ),
                input=f"{prompt}",
            )

            generated_query = response.output_text or "<no_query>"
            result = get_task_result(task, generated_query, task_type)
            task_results.append(result)

        save_task_results(task_results, dataset_name, task_difficulty, task_type, model_name)

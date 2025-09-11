from logging import getLogger

from openai import OpenAI
from tqdm import tqdm

from constants import TASKS_DIRECTORY
from database.neo4j import get_neo4j_schema
from database.sqlite import get_sqlite_tables
from evaluation.scoring import get_task_result
from models import TaskDifficulty, TaskType
from utils import build_remote_prompt, get_tasks_from_json, save_task_results

LIST_DB_TABLES_BY_TASK_TYPE = {
    TaskType.SQL: get_sqlite_tables,
    TaskType.CYPHER: get_neo4j_schema,
}

logger = getLogger(__name__)


def evaluate_remote_model_for_task(
    model_name: str, task_type: TaskType, client: OpenAI
) -> None:
    schema = LIST_DB_TABLES_BY_TASK_TYPE[task_type]()  # type: ignore

    for task_difficulty in TaskDifficulty:
        tasks = get_tasks_from_json(TASKS_DIRECTORY / f"{task_difficulty}.json")
        task_results = []

        for task in tqdm(tasks, f"Tasks ({task_difficulty}, {task_type})"):
            prompt = build_remote_prompt(task_type, task.question, schema)

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a Text-to-{task_type.name} assistant. "
                        f"Return only a valid {task_type.name} query, "
                        "without explanations or other code.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=128,
                temperature=0,
            )

            if not response.choices or not response.choices[0].message.content:
                logger.error(
                    "No response from remote model for question '%s'", task.question
                )
                continue

            generated_query = response.choices[0].message.content.strip()
            result = get_task_result(task, generated_query, task_type)
            task_results.append(result)

        save_task_results(task_results, task_difficulty, task_type, model_name)

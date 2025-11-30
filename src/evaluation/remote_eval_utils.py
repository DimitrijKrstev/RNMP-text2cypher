from models import Task, TaskType, TaskResult
from evaluation.scoring import get_task_result
from evaluation.utils import build_user_prompt, build_sql_system_prompt, build_cypher_system_prompt
from litellm import completion
from logging import getLogger
from tqdm import tqdm

logger = getLogger(__name__)


NO_QUERY = "<no_query>"

prompt_builder = {
    TaskType.SQL: build_sql_system_prompt,
    TaskType.CYPHER: build_cypher_system_prompt,
}


def query_llm(model: str, system: str, prompt: str, api_key: str | None = None) -> str:
    """Query LLM and return generated query string."""
    try:
        response = completion(
            model=model,
            messages=[
            {
                "role": "system",
                "content": system,
                "cache_control": {"type": "ephemeral"} 
            },
            {"role": "user", "content": prompt},
        ],
            api_key=api_key,
        )
        return response.choices[0].message.content or NO_QUERY
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return NO_QUERY


def process_tasks(
    tasks: list[Task],
    task_type: TaskType,
    schema: str,
    db_path: str | None,
    model_name: str,
    api_key: str | None,
) -> list[TaskResult]:
    """Process all tasks and return results."""
    results = []
    system = prompt_builder[task_type](schema)

    for task in tqdm(tasks):
        prompt = build_user_prompt(task.question)
        query = query_llm(model_name, system, prompt, api_key)
        results.append(get_task_result(task, query, task_type, db_path))

    return results

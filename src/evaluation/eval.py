from typing import Any

import torch
from tqdm import tqdm

from constants import TASKS_DIRECTORY
from database.neo4j import get_neo4j_schema
from database.sqlite import get_sqlite_tables
from evaluation.scoring import get_task_result
from models import TaskDifficulty, TaskType
from utils import build_prompt, get_tasks_from_json, save_task_results

LIST_DB_TABLES_BY_TASK_TYPE = {
    TaskType.SQL: get_sqlite_tables,
    TaskType.CYPHER: get_neo4j_schema,
}


def evaluate_model_for_task_type(
    model: Any, tokenizer: Any, task_type: TaskType
) -> None:
    schema = LIST_DB_TABLES_BY_TASK_TYPE[task_type]()  # type: ignore

    for task_difficulty in TaskDifficulty:
        tasks = get_tasks_from_json(TASKS_DIRECTORY / f"{task_difficulty}.json")
        task_results = []

        for task in tqdm(tasks, f"Tasks ({task_difficulty}, {task_type})"):
            prompt = build_prompt(task_type, task.question, schema)
            tokenized_prompt = tokenizer(prompt, return_tensors="pt").to("cuda")

            with torch.inference_mode():
                outputs = model.generate(
                    **tokenized_prompt,
                    max_new_tokens=128,
                    do_sample=False,
                    temperature=None,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id or tokenizer.pad_token_id,
                    use_cache=True,
                    no_repeat_ngram_size=4,
                )

            generated_tokens = outputs[0, tokenized_prompt["input_ids"].size(1) :]
            generated_query = tokenizer.decode(
                generated_tokens, skip_special_tokens=True
            )
            result = get_task_result(task, generated_query, task_type)
            task_results.append(result)

        save_task_results(task_results, task_difficulty, task_type)
        break

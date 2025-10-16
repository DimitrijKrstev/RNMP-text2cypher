from logging import getLogger
from typing import Any

import torch
from tqdm import tqdm

from constants import get_sqlite_db_path, get_tasks_directory
from database.neo4j import get_neo4j_schema
from database.sqlite import get_sqlite_tables
from evaluation.scoring import get_task_result
from models import DatasetName, TaskDifficulty, TaskType
from utils import build_local_prompt, get_tasks_from_json, save_task_results

logger = getLogger(__name__)


def evaluate_local_model_for_task(
    model: Any,
    tokenizer: Any,
    dataset_name: DatasetName,
    task_type: TaskType,
    model_name: str,
) -> None:
    if task_type == TaskType.SQL:
        db_path = get_sqlite_db_path(dataset_name)
        schema = get_sqlite_tables(db_path)
    else:
        schema = get_neo4j_schema()

    tasks_dir = get_tasks_directory(dataset_name)

    for task_difficulty in TaskDifficulty:
        tasks_file = tasks_dir / f"{task_difficulty.value}.json"
        if not tasks_file.exists():
            logger.warning(f"Tasks file not found, skipping: {tasks_file}")
            continue

        tasks = get_tasks_from_json(tasks_file)
        task_results = []

        for task in tqdm(
            tasks, f"Tasks ({dataset_name}, {task_difficulty}, {task_type})"
        ):
            prompt = build_local_prompt(task_type, task.question, schema)
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

        save_task_results(
            task_results, dataset_name, task_difficulty, task_type, model_name
        )

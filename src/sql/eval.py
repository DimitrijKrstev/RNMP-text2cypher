from functools import reduce

import torch

from constants import BASE_MODEL_NAME, TASKS_DIRECTORY
from database.sqlite import get_sqlite_tables
from models import TaskDifficulty
from sql.scoring import get_task_result
from utils import (
    get_tasks_from_json,
    load_model_with_4bit_quantization,
    load_tokenizer,
    save_task_results,
)


def evaluate_sql_model() -> None:
    model = load_model_with_4bit_quantization(BASE_MODEL_NAME)
    tokenizer = load_tokenizer(BASE_MODEL_NAME)
    tables = get_sqlite_tables()
    model.eval()

    for task_difficulty in TaskDifficulty:
        tasks = get_tasks_from_json(TASKS_DIRECTORY / f"{task_difficulty}.json")
        task_results = []

        for task in tasks:
            prompt = (
                "You are a Text-to-SQL assistant. Return ONLY a valid SQL statement. "
                "No explanations, no comments, no code fences.\n\n"
                f"Task: {task.question}\n\n"
                "Schema:\n"
                f"{reduce(lambda acc, t: f'{acc}\n{t}', tables, '')}\n\n"
                "SQL:"
            )
            tokenized_prompt = tokenizer(prompt, return_tensors="pt").to("cuda")

            with torch.inference_mode():
                outputs = model.generate(
                    **tokenized_prompt,
                    max_new_tokens=128,
                    do_sample=False,
                    temperature=None,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id,
                    use_cache=True,
                    no_repeat_ngram_size=4,
                )

            generated_tokens = outputs[-1][tokenized_prompt["input_ids"].shape[-1] :]
            sql_query = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            task_results.append(get_task_result(task, sql_query))

        save_task_results(task_results, task_difficulty)

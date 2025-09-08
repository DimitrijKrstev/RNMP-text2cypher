import json
import os
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from constants import RESULTS_DIRECTORY
from models import Task, TaskDifficulty, TaskResult

HF_TOKEN = os.getenv("HF_TOKEN")


def load_model_with_4bit_quantization(model_name: str) -> Any:
    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=(
            torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        ),
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_cfg,
        token=HF_TOKEN,
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    return model


def load_tokenizer(model_name: str) -> Any:
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    return tokenizer


def get_tasks_from_json(path: Path) -> list[Task]:
    return [Task.from_dict(line) for line in json.load(open(path, "r"))]


def save_task_results(
    task_results: list[TaskResult], task_difficulty: TaskDifficulty
) -> None:
    result_dicts = [task_result.to_dict() for task_result in task_results]

    try:
        with open(RESULTS_DIRECTORY / f"{task_difficulty}.json", "w") as json_file:
            json.dump(result_dicts, json_file)
            json_file.write("\n")
    except Exception as e:
        print(f"Error saving results: {e}")

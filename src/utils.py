import json
import os
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from constants import RESULTS_DIRECTORY
from models import Task, TaskDifficulty, TaskResult, TaskType

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


def get_model_and_tokenizer(model_name: str) -> tuple[Any, Any]:
    model = load_model_with_4bit_quantization(model_name)
    model.eval()
    model.generation_config.top_p = None
    model.generation_config.top_k = None

    tokenizer = load_tokenizer(model_name)
    return model, tokenizer


def get_tasks_from_json(path: Path) -> list[Task]:
    return [Task.from_dict(line) for line in json.load(open(path, "r"))]


def save_task_results(
    task_results: list[TaskResult], task_difficulty: TaskDifficulty, task_type: TaskType
) -> None:
    result_dicts = [task_result.to_dict() for task_result in task_results]

    result_dir = RESULTS_DIRECTORY / task_type.lower()
    result_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(result_dir / f"{task_difficulty}.json", "w") as json_file:
            json.dump(result_dicts, json_file)
            json_file.write("\n")

    except Exception as e:
        print(f"Error saving results: {e}")


def build_prompt(task_type: TaskType, question: str, schema: str) -> str:
    return (
        f"You are a Text-to-{task_type} assistant. Return ONLY a valid {task_type} statement. "
        "No explanations, no comments, no code fences.\n\n"
        "The database schema:\n"
        f"{schema}\n\n"
        f"Your task is to: {question}\n\n"
        f"The {task_type} query:"
    )

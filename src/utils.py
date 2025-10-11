import json
import os
from pathlib import Path
from typing import Any, Tuple 

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel

# Conditional import for BitsAndBytesConfig because of machine compatibility
try:
    if torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
    else:
        class BitsAndBytesConfig:
            def __init__(self, *args, **kwargs):
                raise ImportError("BitsAndBytesConfig is not available because CUDA is not available.")
except ImportError:
    class BitsAndBytesConfig:
        def __init__(self, *args, **kwargs):
            raise ImportError("BitsAndBytesConfig is not installed.")
        

from constants import RESULTS_DIR
from models import Task, TaskDifficulty, TaskResult, TaskType

HF_TOKEN = os.getenv("HF_TOKEN")

def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"
    else:
        return "cpu"


def load_model_for_device(model_name: str, device: str) -> PreTrainedModel:
    device = get_device()
    print(f"Loading model {model_name} on device: {device}")

    model_kwargs = {
        "token": HF_TOKEN,
        "low_cpu_mem_usage": True,
        "device_map": "auto" if device == "mps" else None,
    }

    if device == "cuda":
        # Apply 4bit quantization for CUDA
        bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=(
            torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        ),
    )
        model_kwargs['quantization_config'] = bnb_cfg
        model_kwargs["torch_dtype"] = (
            torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        )
    elif device == "mps":
        # Config for apple silicon
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            model_kwargs["torch_dtype"] = torch.bfloat16
            model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            return model.to(device)
        else:
            model_kwargs["torch_dtype"] = torch.float32
    else:
        print("Warning: Using CPU for inference. This may be slow.")
        model_kwargs["torch_dtype"] = torch.float32


    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

    return model

# def load_model_with_4bit_quantization(model_name: str) -> Any:
#     bnb_cfg = BitsAndBytesConfig(
#         load_in_4bit=True,
#         bnb_4bit_use_double_quant=True,
#         bnb_4bit_quant_type="nf4",
#         bnb_4bit_compute_dtype=(
#             torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
#         ),
#     )

#     model = AutoModelForCausalLM.from_pretrained(
#         model_name,
#         quantization_config=bnb_cfg,
#         token=HF_TOKEN,
#         device_map="auto",
#         low_cpu_mem_usage=True,
#     )

#     return model

def load_tokenizer(model_name: str) -> Any:
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    return tokenizer


def get_model_and_tokenizer(model_name: str) -> tuple[Any, Any]:
    model = load_model_for_device(model_name)
    model.eval()
    # model.generation_config.top_p = None
    # model.generation_config.top_k = None

    tokenizer = load_tokenizer(model_name)
    return model, tokenizer


def get_tasks_from_json(path: Path) -> list[Task]:
    return [Task.from_dict(line) for line in json.load(open(path, "r"))]


def save_task_results(
    task_results: list[TaskResult],
    dataset_name: str,
    task_difficulty: TaskDifficulty,
    task_type: TaskType,
    model_name: str,
) -> None:
    result_dicts = [task_result.to_dict() for task_result in task_results]

    model_name_slug = model_name.replace("/", "_")
    result_dir = (
        RESULTS_DIR
        / dataset_name
        / task_type.value.lower()
        / model_name_slug
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    file_path = result_dir / f"{task_difficulty.value}.json"

    try:
        with open(file_path, "w") as json_file:
            json.dump(result_dicts, json_file, indent=2)
            json_file.write("\n")
        print(f"Saved results to {file_path}")

    except Exception as e:
        print(f"Error saving results: {e}")


def build_local_prompt(task_type: TaskType, question: str, schema: str) -> str:
    return (
        f"You are a Text-to-{task_type} assistant. Return ONLY a valid {task_type} statement. "
        "No explanations, no comments, no code fences.\n"
        "Do NOT order results unless explicitly asked.\n"
        "Do NOT use column or table aliases unless explicitly asked.\n"
        "Do NOT use 'AS' for aggregate functions like COUNT, SUM, AVG, etc. unless explicitly asked\n"
        "Do NOT return DISTINCT values unless explicitly asked.\n"
        "The database schema:\n"
        f"{schema}\n"
        "Dates are in format 'YYYY-MM-DD HH:MM:SS'\n\n"
        f"Your task is to: {question}\n\n"
        f"The {task_type} query:"
    )


def build_remote_prompt(task_type: TaskType, question: str, schema: str) -> str:
    return (
        "Here is my database schema:\n"
        f"{schema}\n"
        "Dates are in format 'YYYY-MM-DD HH:MM:SS'\n\n"
        f"Your task is to create a {task_type} query that will: {question}\n\n"
    )

import os
from logging import basicConfig, getLogger, INFO
from pathlib import Path
from dotenv import load_dotenv

import typer
from openai import OpenAI

from constants import BASE_MODEL_NAME, REMOTE_MODEL_NAME
from database.neo4j import get_neo4j_schema
from database.setup import get_node_csvs, load_dataset_to_sqlite
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from models import DatasetName, TaskType
from utils import get_model_and_tokenizer
from validate_tasks import validate


load_dotenv()  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


app = typer.Typer()

basicConfig(level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)


@app.command()
def generate_csvs(dataset_name: DatasetName) -> None:
    get_node_csvs(dataset_name)


@app.command()
def load_sqlite(dataset_name: DatasetName) -> None:
    load_dataset_to_sqlite(dataset_name)


@app.command()
def validate_tasks(dataset_name: DatasetName) -> None:
    for path in Path(f"src/tasks/{dataset_name}").glob("*.json"):
        validate(path, dataset_name)


@app.command()
def get_neo4j() -> None:
    schema = get_neo4j_schema()
    logger.info(schema)


@app.command()
def evaluate_local(dataset_name: DatasetName, task_types: list[TaskType]) -> None:
    model, tokenizer = get_model_and_tokenizer(BASE_MODEL_NAME)
    model_short_name = BASE_MODEL_NAME.split("/")[-1]

    for task_type in task_types:
        evaluate_local_model_for_task(
            model, tokenizer, dataset_name, task_type, model_short_name
        )


@app.command()
def evaluate_remote(dataset_name: DatasetName, task_types: list[TaskType]) -> None:
    
    if not OPENAI_API_KEY:
        raise typer.Abort("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=OPENAI_API_KEY)
    for task_type in task_types:
        evaluate_remote_model_for_task(
            REMOTE_MODEL_NAME, dataset_name, task_type, client
        )


if __name__ == "__main__":
    app()

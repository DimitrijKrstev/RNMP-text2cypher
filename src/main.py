import os
from logging import basicConfig, getLogger, INFO
from pathlib import Path
from dotenv import load_dotenv

import typer
from openai import OpenAI

from constants import BASE_MODEL_NAME, REMOTE_MODEL_NAME
from database.neo4j import get_neo4j_schema
from database.setup import get_node_csvs, load_dataset_to_sqlite, load_dataset_to_duckdb
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from evaluation.re_evaluation import re_evaluate_sql_results
from models import DatasetName, TaskType
from utils import get_model_and_tokenizer
from validate_tasks import validate

load_dotenv()  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = typer.Typer()

basicConfig(level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)


@app.command()
def generate_csvs(dataset_name: DatasetName, sample_size: float = 1.0) -> None:
    """Generate CSVs for Neo4j import."""
    get_node_csvs(dataset_name, sample_size)


@app.command()
def load_sqlite(dataset_name: DatasetName) -> None:
    """Create/refresh the SQLite DB. Not used/replaced by DuckDB."""
    load_dataset_to_sqlite(dataset_name)


@app.command()
def load_duckdb(dataset_name: DatasetName, sample_size: float = 1.0) -> None:
    """Create/refresh the DuckDB."""
    load_dataset_to_duckdb(dataset_name, sample_size)


@app.command()
def validate_tasks(dataset_name: DatasetName) -> None:
    """Validate all tasks."""
    for path in Path(f"src/tasks/{dataset_name}").glob("*.json"):
        validate(path, dataset_name)


@app.command()
def get_neo4j() -> None:
    """Get Neo4j schema."""
    schema = get_neo4j_schema()
    logger.info(schema)


@app.command()
def re_evaluate_results(
    dataset_name: DatasetName, 
    task_type: TaskType = TaskType.SQL
) -> None:
    """Re-evaluate existing results."""
    if task_type == TaskType.CYPHER:
        # TODO implement cypher re-evaluation
        logger.info("Cypher re-evaluation not yet implemented")
    else:
        re_evaluate_sql_results(dataset_name)


@app.command()
def evaluate_local(dataset_name: DatasetName, task_types: list[TaskType]) -> None:
    """Evaluate the local text2SQL model."""
    model, tokenizer = get_model_and_tokenizer(BASE_MODEL_NAME)
    model_short_name = BASE_MODEL_NAME.split("/")[-1]

    for task_type in task_types:
        evaluate_local_model_for_task(
            model, tokenizer, dataset_name, task_type, model_short_name
        )


@app.command()
def evaluate_remote(dataset_name: DatasetName, task_types: list[TaskType]) -> None:
    """Evaluate the remote LLM model."""
    if not OPENAI_API_KEY:
        raise typer.Abort("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=OPENAI_API_KEY)

    for task_type in task_types:
        evaluate_remote_model_for_task(
            REMOTE_MODEL_NAME, dataset_name, task_type, client
        )

@app.command()
def plot_evaluation_results(dataset_name: DatasetName) -> None:
    """Plot evaluation results."""
    from evaluation.plot import plot_results

    plot_results(dataset_name)

if __name__ == "__main__":
    app()
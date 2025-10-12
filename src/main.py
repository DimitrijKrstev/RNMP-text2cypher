import os
from pathlib import Path

import typer
from openai import OpenAI
from typing_extensions import Annotated

from constants import BASE_MODEL_NAME, REMOTE_MODEL_NAME
from database.neo4j import get_neo4j_schema
from database.setup import get_node_csvs, load_dataset_to_sqlite
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from models import TaskType
from utils import get_model_and_tokenizer
from validate_tasks import validate


app = typer.Typer(help="RNMP Text-to-Query CLI")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.command()
def generate_csvs(
    dataset_name: Annotated[
        str,
        typer.Option(
            "--dataset",
            "-d",
            help="The name of the rel-bench dataset (e.g., 'rel-f1', 'rel-stack').",
        ),
    ],
):
    """Generate CSVs for Neo4j import."""
    print(f"--- Generating CSVs for dataset: {dataset_name} ---")
    get_node_csvs(dataset_name)
    print("\n CSV generation complete.")
    print(
        f" Next, run the Neo4j docker-compose to import the CSVs from 'neo4j/import/{dataset_name}/'"
    )


@app.command()
def load_sqlite(
    dataset_name: Annotated[
        str,
        typer.Option(
            "--dataset",
            "-d",
            help="The name of the rel-bench dataset (e.g., 'rel-f1', 'rel-stack').",
        ),
    ],
):
    """Create/refresh the SQLite database."""
    print(f"--- Loading dataset into SQLite: {dataset_name} ---")
    load_dataset_to_sqlite(dataset_name)
    print("\n SQLite database loaded successfully.")
    print(" You can now run SQL queries against the database.")


@app.command()
def setup_data(
    dataset_name: Annotated[
        str,
        typer.Option(
            "--dataset",
            "-d",
            help="The name of the rel-bench dataset (e.g., 'rel-f1', 'rel-stack').",
        ),
    ],
):
    """Downloads and prepares a dataset for both SQLite and Neo4j."""
    print(f"--- Setting up data for dataset: {dataset_name} ---")
    load_dataset_to_sqlite(dataset_name)
    print(" SQLite database loaded.")

    get_node_csvs(dataset_name)
    print(" CSVs generated for Neo4j.")

    print("\n Setup complete.")
    print(
        f" Next, run the Neo4j docker-compose to import the CSVs from 'neo4j/import/{dataset_name}/'"
    )


@app.command()
def get_schema():
    """Get and display the Neo4j database schema."""
    print("--- Fetching Neo4j schema ---")
    schema = get_neo4j_schema()
    print("\n" + schema)
    print("\n Schema fetched successfully.")


@app.command()
def validate_tasks(
    tasks_path: Annotated[
        str,
        typer.Option(
            "--tasks",
            "-t",
            help="Path to the JSON file containing tasks to validate.",
        ),
    ] = "src/tasks/*.json",
    database_name: Annotated[
        str,
        typer.Option(
            "--database",
            "-d",
            help="The name of the rel-bench dataset (e.g., 'rel-f1', 'rel-stack').",
        ),
    ] = "rel-f1",
):
    """Validates tasks by checking if their SQL and Cypher queries return results."""
    print(f"--- Validating tasks in {tasks_path} ---")

    # Handle glob patterns
    if "*" in tasks_path:
        paths = Path().glob(tasks_path)
        for path in paths:
            print(f"\nValidating {path}...")
            validate(path, database_name)
    else:
        validate(Path(tasks_path), database_name)

    print("\n Validation complete.")


@app.command()
def evaluate_local(
    dataset_name: Annotated[
        str,
        typer.Option("--dataset", "-d", help="The dataset to evaluate against."),
    ],
    task_type: Annotated[
        TaskType,
        typer.Option(
            "--type", "-t", help="The query language to generate (sql/cypher)."
        ),
    ],
    model_name: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="The local model name/path to use.",
        ),
    ] = BASE_MODEL_NAME,
):
    """Evaluate a local model for SQL or Cypher generation."""
    print(f"--- Running local evaluation for {task_type.value} on {dataset_name} ---")
    print(f"Loading model: {model_name}")

    model, tokenizer = get_model_and_tokenizer(model_name)
    model_short_name = model_name.split("/")[-1]

    evaluate_local_model_for_task(
        model, tokenizer, dataset_name, task_type, model_short_name
    )

    print(f"\n Local evaluation complete.")
    print(f" Check the results in the output directory.")


@app.command()
def evaluate_remote(
    dataset_name: Annotated[
        str,
        typer.Option("--dataset", "-d", help="The dataset to evaluate against."),
    ],
    task_type: Annotated[
        TaskType,
        typer.Option(
            "--type", "-t", help="The query language to generate (sql/cypher)."
        ),
    ],
    model_name: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="The remote model name to use.",
        ),
    ] = REMOTE_MODEL_NAME,
):
    """Evaluate a remote LLM (e.g., OpenAI) for SQL or Cypher generation."""
    print(f"--- Running remote evaluation for {task_type.value} on {dataset_name} ---")
    print(f"Using model: {model_name}")

    if not OPENAI_API_KEY:
        print(" Error: OPENAI_API_KEY environment variable not set.")
        raise typer.Exit(code=1)

    client = OpenAI(api_key=OPENAI_API_KEY)
    evaluate_remote_model_for_task(model_name, dataset_name, task_type, client)

    print(f"\n Remote evaluation complete.")
    print(f" Check the results in the output directory.")


@app.command()
def evaluate(
    dataset_name: Annotated[
        str, typer.Option("--dataset", "-d", help="The dataset to evaluate against.")
    ],
    task_type: Annotated[
        TaskType, typer.Option("--type", "-t", help="The query language to generate.")
    ],
    eval_type: Annotated[
        str,
        typer.Option(
            "--eval",
            "-e",
            help="The evaluation type ('remote' or 'local').",
        ),
    ] = "remote",
    model_name: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="The model name/path to use.",
        ),
    ] = None,
):
    """Runs the evaluation against a remote or local model (unified command)."""
    if eval_type == "remote":
        model = model_name or REMOTE_MODEL_NAME
        print(
            f"--- Running remote evaluation for {task_type.value} on {dataset_name} ---"
        )
        if not OPENAI_API_KEY:
            print(" Error: OPENAI_API_KEY environment variable not set.")
            raise typer.Exit(code=1)
        client = OpenAI(api_key=OPENAI_API_KEY)
        evaluate_remote_model_for_task(model, dataset_name, task_type, client)
    elif eval_type == "local":
        model = model_name or BASE_MODEL_NAME
        print(
            f"--- Running local evaluation for {task_type.value} on {dataset_name} ---"
        )
        model_obj, tokenizer = get_model_and_tokenizer(model)
        model_short_name = model.split("/")[-1]
        evaluate_local_model_for_task(
            model_obj, tokenizer, dataset_name, task_type, model_short_name
        )
    else:
        print(
            f" Error: Unknown evaluation type '{eval_type}'. Use 'remote' or 'local'."
        )
        raise typer.Exit(code=1)

    print(f"\n Evaluation complete.")
    print(f"Check the results in the output directory.")


if __name__ == "__main__":
    app()

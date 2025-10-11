import typer
from typing_extensions import Annotated

from database.setup import get_node_csvs, load_dataset_to_sqlite
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from models import TaskType

app = typer.Typer()


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
    get_node_csvs(dataset_name)
    print("\nSetup complete.")
    print(
        f"Next, run the Neo4j docker-compose to import the CSVs from 'neo4j/import/{dataset_name}/'"
    )


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
):
    """Runs the evaluation against a remote or local model."""
    print(
        f"--- Running {eval_type} evaluation for {task_type.value} on {dataset_name} ---"
    )
    if eval_type == "remote":
        evaluate_remote_model_for_task(dataset_name, task_type)
    elif eval_type == "local":
        print("Local evaluation not fully implemented in this example yet.")
    else:
        print(f"Error: Unknown evaluation type '{eval_type}'. Use 'remote' or 'local'.")


if __name__ == "__main__":
    app()

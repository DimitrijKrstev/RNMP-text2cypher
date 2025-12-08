import os
from logging import basicConfig, getLogger, INFO
from pathlib import Path
from dotenv import load_dotenv

import typer
from typing import Optional

from constants import REMOTE_MODEL_NAME
from database.neo4j import get_neo4j_schema
from database.duckdb import get_duckdb_schema
from database.setup import get_node_csvs, load_dataset_to_duckdb
from evaluation.re_evaluation import re_evaluate_results
from evaluation.remote_eval import evaluate_remote_model
from models import DatasetName, TaskType
from validate_tasks import validate

load_dotenv()  
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = typer.Typer()

basicConfig(level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)


@app.command()
def generate_csvs(dataset_name: DatasetName, sample_size: float = 1.0) -> None:
    """Generate CSVs for Neo4j import."""
    get_node_csvs(dataset_name, sample_size)


@app.command()
def load_duckdb(dataset_name: DatasetName, sample_size: float = 1.0) -> None:
    """Create/refresh the DuckDB."""
    load_dataset_to_duckdb(dataset_name, sample_size)


@app.command()
def validate_tasks(
    dataset_name: DatasetName,
    task_types: Optional[list[TaskType]] = typer.Argument(default=None),
) -> None:
    if task_types is None:
        task_types = [TaskType.SQL, TaskType.CYPHER]
    
    for path in Path(f"src/tasks/{dataset_name}").glob("*.json"):
        validate(path, dataset_name, task_types)


@app.command()
def get_neo4j() -> None:
    """Get Neo4j schema."""
    schema = get_neo4j_schema()
    logger.info(schema)


@app.command()
def re_evaluation(
    dataset_name: DatasetName, 
    task_type: TaskType = TaskType.SQL
) -> None:
    """Re-evaluate existing results."""
    re_evaluate_results(dataset_name, task_type)


@app.command()
def evaluate_remote(dataset_name: DatasetName, task_types: list[TaskType]) -> None:
    """Evaluate the remote LLM model."""
    if not ANTHROPIC_API_KEY:
        raise typer.Abort("API key environment variable not set!")

    for task_type in task_types:
        evaluate_remote_model(
            REMOTE_MODEL_NAME, dataset_name, task_type, ANTHROPIC_API_KEY
        )

@app.command()
def plot_evaluation_results(dataset_name: DatasetName) -> None:
    """Plot evaluation results."""
    from evaluation.plot import plot_results

    plot_results(dataset_name)

@app.command()
def generate_schema(dataset_name: DatasetName, task_types : list[TaskType]) -> None:
    """Helpher method used through UI to generate Schemas of databases"""
    print('---------------------------------------------')     
    for task_type in task_types:
        result = (
        get_neo4j_schema()
        if task_type == TaskType.CYPHER
        else get_duckdb_schema(dataset_name, format=True)
    )
        print(f'------------------{task_type}---------------------')
        print('---------------------------------------------')
        print(result)
        print('---------------------------------------------')     

@app.command()
def generate_thesis_plots() -> None:
    """Generate all thesis plots and tables"""
    from evaluation.complete_plot import ThesisPlotter
    from constants import RESULTS_DIR, PROJECT_ROOT
    
    output_dir = PROJECT_ROOT / "plots"
    plotter = ThesisPlotter(RESULTS_DIR, output_dir)
    plotter.generate_all_plots()

if __name__ == "__main__":
    app()
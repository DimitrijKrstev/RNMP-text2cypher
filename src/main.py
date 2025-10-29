import os
import sys
from argparse import ArgumentParser
from logging import INFO, basicConfig
from pathlib import Path

from openai import OpenAI

from constants import BASE_MODEL_NAME, REMOTE_MODEL_NAME
from database.neo4j import get_neo4j_schema
from database.setup import get_node_csvs, load_dataset_to_sqlite, load_dataset_to_duckdb
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from models import TaskType
from utils import get_model_and_tokenizer
from validate_tasks import validate

basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser():
    parser = ArgumentParser(prog="rnmp")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    for name, func, help_text, needs_dataset in COMMANDS:
        cmd = subparsers.add_parser(name, help=help_text)
        cmd.set_defaults(func=func)
        if needs_dataset:
            add_dataset_arg(cmd)

    return parser


def add_dataset_arg(cmd):
    cmd.add_argument(
        "--dataset-name",
        type=str,
        default="rel-f1",
        help="Name of the RelBench dataset to use.",
        choices=["rel-f1", "rel-stack"],
    )


def generate_csvs(args):
    get_node_csvs(args.dataset_name)


def get_neo4j_schema_command(_):
    schema = get_neo4j_schema()
    print(schema)


def load_sqlite(args):
    load_dataset_to_sqlite(args.dataset_name)

def load_duckdb(args):
    load_dataset_to_duckdb(args.dataset_name)

def validate_tasks(_):
    for path in Path("src/tasks").glob("*.json"):
        validate(path)


def evaluate_local_model(_):
    model, tokenizer = get_model_and_tokenizer(BASE_MODEL_NAME)

    evaluate_local_model_for_task(
        model, tokenizer, TaskType.SQL, BASE_MODEL_NAME.split("/")[-1]
    )
    evaluate_local_model_for_task(
        model, tokenizer, TaskType.CYPHER, BASE_MODEL_NAME.split("/")[-1]
    )


def evaluate_remote_model(_):
    client = OpenAI(api_key=OPENAI_API_KEY)

    evaluate_remote_model_for_task(REMOTE_MODEL_NAME, TaskType.SQL, client)
    evaluate_remote_model_for_task(REMOTE_MODEL_NAME, TaskType.CYPHER, client)


COMMANDS = [
    (
        "generate-csvs",
        generate_csvs,
        "Generate CSVs for Neo4j import.",
        True,
    ),
    (
        "load-sqlite",
        load_sqlite,
        "Create/refresh the SQLite DB.",
        True,
    ),
    (
        "load-duckdb",           
        load_duckdb,             
        "Create/refresh the DuckDB.",  
        True,                    
    ),                           
    (
        "validate-tasks",
        validate_tasks,
        "Validate all tasks.",
        False,
    ),
    (
        "get-neo4j",
        get_neo4j_schema_command,
        "Get Neo4j schema.",
        False,
    ),
    (
        "evaluate-local-model",
        evaluate_local_model,
        "Evaluate the text2SQL model.",
        False,
    ),
    (
        "evaluate-remote-model",
        evaluate_remote_model,
        "Evaluate the remote LLM model.",
        False,
    ),
]


if __name__ == "__main__":
    sys.exit(main())

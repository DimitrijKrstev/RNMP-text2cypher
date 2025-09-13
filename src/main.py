import os
import sys
from argparse import ArgumentParser
from logging import INFO, basicConfig
from pathlib import Path

from openai import OpenAI

from constants import BASE_MODEL_NAME, REMOTE_MODEL_NAME
from database.setup import get_node_csvs, load_dataset_to_sqlite
from evaluation.local_eval import evaluate_local_model_for_task
from evaluation.remote_eval import evaluate_remote_model_for_task
from models import TaskType
from utils import get_model_and_tokenizer
from validate_tasks import validate

basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def build_parser():
    args = ArgumentParser(prog="rnmp")
    sub = args.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "generate-csvs", help="Generate CSVs for Neo4j import."
    ).set_defaults(func=generate_csvs)

    sub.add_parser("load-sqlite", help="Create/refresh the SQLite DB.").set_defaults(
        func=load_sqlite
    )

    sub.add_parser(
        "evaluate-local-model", help="Evaluate the text2SQL model."
    ).set_defaults(func=evaluate_local_model)

    sub.add_parser(
        "evaluate-remote-model", help="Evaluate the remote LLM model."
    ).set_defaults(func=evaluate_remote_model)

    sub.add_parser("validate-tasks", help="Validate all tasks.").set_defaults(
        func=validate_tasks
    )

    return args


def generate_csvs(_):
    get_node_csvs()


def load_sqlite(_):
    load_dataset_to_sqlite()


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


def validate_tasks(_):
    for path in Path("src/tasks").glob("*.json"):
        validate(path)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

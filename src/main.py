import sys
from argparse import ArgumentParser
from logging import INFO, basicConfig

from database.setup import get_node_csvs, load_dataset_to_sqlite
from sql.eval import evaluate_sql_model

basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def build_parser():
    args = ArgumentParser(prog="rnmp")
    sub = args.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "generate-csvs", help="Generate CSVs for Neo4j import."
    ).set_defaults(func=generate_csvs)

    sub.add_parser("load-sqlite", help="Create/refresh the SQLite DB.").set_defaults(
        func=load_sqlite
    )

    sub.add_parser("evaluate-model", help="Evaluate the text2SQL model.").set_defaults(
        func=evaluate_model
    )

    return args


def generate_csvs(_):
    get_node_csvs()


def load_sqlite(_):
    load_dataset_to_sqlite()


def evaluate_model(_):
    evaluate_sql_model()


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

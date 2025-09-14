import json
from pathlib import Path

from database.neo4j import query_neo4j
from database.sqlite import query_sqlite
from models import Task


def validate(tasks_path: Path) -> None:
    with open(tasks_path, "r") as f:
        tasks = [Task.from_dict(task) for task in json.load(f)]

    valid_tasks = set()

    for task in tasks:
        sql = task.sql
        cypher = task.cypher

        sql_valid = False
        cypher_valid = False

        try:
            sql_result = query_sqlite(sql)
            if sql_result:
                sql_valid = True
        except Exception as e:
            print(f"SQL query failed: {e}")

        cypher_result = []

        try:
            cypher_result = query_neo4j(cypher)
            if cypher_result:
                cypher_valid = True
        except Exception as e:
            print(f"Cypher query failed: {e}")

        if sql_valid and cypher_valid:
            valid_tasks.add(task)

    print(
        f"In path {tasks_path}, found {len(tasks)} tasks, {len(valid_tasks)} valid tasks."
    )

    for task in tasks:
        if task not in valid_tasks:
            print(f"Invalid task: {task.question}")
            print(f"SQL: {task.sql}")
            print(f"Cypher: {task.cypher}")
            print()

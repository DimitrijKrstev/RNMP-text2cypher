import json
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from constants import get_duckdb_path
from database.neo4j import query_neo4j
from database.duckdb import query_duckdb
from models import DatasetName, Task, TaskType

QUERY_DB_BY_TASK_TYPE = {
    TaskType.SQL: query_duckdb,
    TaskType.CYPHER: query_neo4j,
}


def validate(
    tasks_path: Path,
    database_name: DatasetName,
    task_types: Optional[list[TaskType]] = None,
) -> None:

    if task_types is None:
        task_types = [TaskType.SQL, TaskType.CYPHER]

    with open(tasks_path, "r") as f:
        tasks = [Task.from_dict(task) for task in json.load(f)]

    db_path = get_duckdb_path(database_name)
    valid_tasks: set[Task] = set()
    invalid_tasks: dict[Task, dict[TaskType, str]] = {}

    for task in tqdm(tasks, desc=f"Validating {tasks_path.stem}", unit="task"):
        errors: dict[TaskType, str] = {}

        for task_type in task_types:
            query = task.sql if task_type == TaskType.SQL else task.cypher
            query_fn = QUERY_DB_BY_TASK_TYPE[task_type]

            try:
                args = (query, db_path) if task_type == TaskType.SQL else (query,)
                result = query_fn(*args)
                if not result:
                    errors[task_type] = "Empty result"
            except Exception as e:
                errors[task_type] = str(e)

        if not errors:
            valid_tasks.add(task)
        else:
            invalid_tasks[task] = errors

    print()
    print(f"Path: {tasks_path}")
    print(f"Total: {len(tasks)} | Valid: {len(valid_tasks)} | Invalid: {len(invalid_tasks)}")
    print(f"Validated: {', '.join(t.value for t in task_types)}")
    print()

    for task, errors in invalid_tasks.items():
        print(f"❌ {task.question}")
        for task_type, error in errors.items():
            query = task.sql if task_type == TaskType.SQL else task.cypher
            print(f"   [{task_type.value}] {error}")
            print(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        print()
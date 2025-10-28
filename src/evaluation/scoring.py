from re import sub

import sqlparse

from database.neo4j import query_neo4j
from database.sqlite import query_sqlite
from models import Task, TaskResult, TaskType

QUERY_DB_BY_TASK_TYPE = {
    TaskType.SQL: query_sqlite,
    TaskType.CYPHER: query_neo4j,
}


def get_task_result(task: Task, model_response: str, task_type: TaskType, db_path: str) -> TaskResult:
    syntaxically_correct = False
    correct_result = False
    exact_match = False

    try:
        result = QUERY_DB_BY_TASK_TYPE[task_type](model_response, db_path)  # type: ignore
        syntaxically_correct = True
        optimal_response = task.get_response_by_task_type(task_type)

        if result == QUERY_DB_BY_TASK_TYPE[task_type](optimal_response, db_path):  # type: ignore
            correct_result = True
        if normalize_query(model_response, task_type) == normalize_query(
            optimal_response, task_type
        ):
            exact_match = True

    finally:
        return TaskResult(
            task,
            model_response,
            syntaxically_correct,
            correct_result,
            exact_match,
            task_type,
        )


def normalize_query(query: str, task_type: TaskType) -> str:
    query = query.strip().lower()

    query = sub(r"\s+", " ", query)

    if task_type == TaskType.SQL:
        parsed = sqlparse.format(
            query,
            keyword_case="lower",
            identifier_case="lower",
            strip_comments=True,
            reindent=False,
        )
        query = sub(r"\s+", " ", parsed).strip()

    elif task_type == TaskType.CYPHER:
        query = sub(r"\s+as\s+\w+", "", query)
        query = query.strip()

    query = query.rstrip(";")

    return query

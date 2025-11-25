from re import sub
from logging import getLogger
import sqlparse

from database.neo4j import query_neo4j
from database.sqlite import query_sqlite
from database.duckdb import query_duckdb
from models import Task, TaskResult, TaskType, SQLQueryAnalyzer, CypherQueryAnalyzer

logger = getLogger(__name__)

ANALYZERS = {
    TaskType.SQL: SQLQueryAnalyzer(),
    TaskType.CYPHER: CypherQueryAnalyzer()
}

QUERY_DB_BY_TASK_TYPE = {
    TaskType.SQL: query_duckdb,
    TaskType.CYPHER: query_neo4j,
}

def get_task_result(task: Task, model_response: str, task_type: TaskType, db_path: str) -> TaskResult:
    syntaxically_correct = False
    correct_result = False
    exact_match = False

    analyzer = ANALYZERS[task_type]
    if not analyzer.is_valid(model_response):
        pass

    tables = analyzer.get_entities(model_response)
    attributes = analyzer.get_attributes(model_response)
    relations = analyzer.get_relations(model_response)
    filters = analyzer.get_filters(model_response)
    aggregations = analyzer.get_aggregations(model_response)

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
    except Exception as e:
        logger.error(f"Error: {e}")

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

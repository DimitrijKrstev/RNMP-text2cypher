from database.neo4j import query_neo4j
from database.sqlite import query_sqlite
from models import Task, TaskResult, TaskType

QUERY_DB_BY_TASK_TYPE = {
    TaskType.SQL: query_sqlite,
    TaskType.CYPHER: query_neo4j,
}


def get_task_result(task: Task, model_response: str, task_type: TaskType) -> TaskResult:
    syntaxically_correct = False
    correct_result = False
    cannonical_match = False  # TODO
    exact_match = False

    try:
        result = QUERY_DB_BY_TASK_TYPE[task_type](model_response)  # type: ignore
        syntaxically_correct = True
        optimal_response = task.get_response_by_task_type(task_type)

        if result == QUERY_DB_BY_TASK_TYPE[task_type](optimal_response):  # type: ignore
            correct_result = True
        if model_response == optimal_response:
            exact_match = True

    finally:
        return TaskResult(
            task,
            model_response,
            syntaxically_correct,
            correct_result,
            cannonical_match,
            exact_match,
            task_type,
        )

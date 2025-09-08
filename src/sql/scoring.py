from database.sqlite import query_sqlite
from models import Task, TaskResult


def get_task_result(task: Task, response: str) -> TaskResult:
    syntaxically_correct = False
    correct_result = False
    cannonical_match = False  # TODO
    exact_match = False

    try:
        result = query_sqlite(response)
        syntaxically_correct = True
        if result == query_sqlite(task.sql):
            correct_result = True
        if response == task.sql:
            exact_match = True

    finally:
        return TaskResult(
            task,
            response,
            syntaxically_correct,
            correct_result,
            cannonical_match,
            exact_match,
        )

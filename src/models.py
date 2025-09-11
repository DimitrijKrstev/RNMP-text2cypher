from dataclasses import dataclass
from enum import StrEnum
from functools import reduce


@dataclass(slots=True, frozen=True)
class Task:
    question: str
    sql: str
    cypher: str

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            question=data["question"],
            sql=data["sql"],
            cypher=data["cypher"],
        )

    def get_response_by_task_type(self, task_type: "TaskType") -> str:
        if task_type == TaskType.SQL:
            return self.sql
        elif task_type == TaskType.CYPHER:
            return self.cypher


@dataclass(slots=True, frozen=True)
class TaskResult:
    task: Task
    response: str
    syntaxically_correct: bool
    correct_result: bool
    cannonical_match: bool
    exact_match: bool
    task_type: "TaskType"

    def to_dict(self) -> dict:
        return {
            "question": self.task.question,
            "expected_script": (
                self.task.sql if self.task_type == TaskType.SQL else self.task.cypher
            ),
            "generated_script": self.response,
            "syntaxically_correct": self.syntaxically_correct,
            "correct_result": self.correct_result,
            "cannonical_match": self.cannonical_match,
            "exact_match": self.exact_match,
        }


class TaskDifficulty(StrEnum):
    EASY = "easy"
    INTERMEDIATE = "intermediate"
    HARD = "hard"


class TaskType(StrEnum):
    SQL = "SQL"
    CYPHER = "Cypher"


@dataclass(slots=True, frozen=True)
class SQLTableWithHeaders:
    table: str
    columns: list[str]

    def __repr__(self) -> str:
        cols = reduce(
            lambda acc, col: f"{acc},{col}", self.columns[1:], self.columns[0]
        )
        return f"{self.table}({cols})"


@dataclass
class GraphEntity:
    name: str
    properties: list[str]

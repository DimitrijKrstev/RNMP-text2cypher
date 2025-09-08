from dataclasses import dataclass
from enum import StrEnum
from functools import reduce


@dataclass(slots=True, frozen=True)
class Task:
    question: str
    sql: str

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            question=data["question"],
            sql=data["sql"],
        )


@dataclass(slots=True, frozen=True)
class TaskResult:
    task: Task
    response: str
    syntaxically_correct: bool
    correct_result: bool
    cannonical_match: bool
    exact_match: bool

    def to_dict(self) -> dict:
        return {
            "question": self.task.question,
            "expected_sql_script": self.task.sql,
            "generated_sql_script": self.response,
            "syntaxically_correct": self.syntaxically_correct,
            "correct_result": self.correct_result,
            "cannonical_match": self.cannonical_match,
            "exact_match": self.exact_match,
        }


class TaskDifficulty(StrEnum):
    EASY = "easy"
    INTERMEDIATE = "intermediate"
    HARD = "hard"


@dataclass(slots=True, frozen=True)
class SQLTableWithHeaders:
    table: str
    columns: list[str]

    def __repr__(self) -> str:
        cols = reduce(
            lambda acc, col: f"{acc},{col}", self.columns[1:], self.columns[0]
        )
        return f"{self.table}({cols})"

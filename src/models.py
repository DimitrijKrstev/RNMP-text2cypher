from dataclasses import dataclass
from enum import StrEnum
from functools import reduce


@dataclass(slots=True, frozen=True)
class Task:
    question: str
    sql: str
    cypher: str
    cypher_result: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            question=data["question"],
            sql=data["sql"],
            cypher=data["cypher"],
            cypher_result=data.get("cypher_result"),
        )

    def to_dict(self):
        return {
            "question": self.question,
            "sql": self.sql,
            "cypher": self.cypher,
            "cypher_result": self.cypher_result,
        }

    def get_response_by_task_type(self, task_type: "TaskType") -> str:
        if task_type == TaskType.SQL:
            return self.sql
        elif task_type == TaskType.CYPHER:
            return self.cypher

    def __hash__(self):
        return hash(self.question)


@dataclass(slots=True, frozen=True)
class TaskResult:
    task: Task
    response: str
    syntaxically_correct: bool
    correct_result: bool
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
            "exact_match": self.exact_match,
        }

    @classmethod
    def from_dict(cls, data: dict, task_type: "TaskType") -> "TaskResult":
        task = Task(
            question=data["question"],
            sql=data["sql"] if "sql" in data else "",
            cypher=data["cypher"] if "cypher" in data else "",
            cypher_result=data.get("cypher_result"),
        )
        return cls(
            task=task,
            response=data["generated_script"],
            syntaxically_correct=data["syntaxically_correct"],
            correct_result=data["correct_result"],
            exact_match=data["exact_match"],
            task_type=task_type,
        )


class DatasetName(StrEnum):
    REL_F1 = "rel-f1"
    REL_STACK = "rel-stack"


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

from functools import reduce
from pathlib import Path
from sqlite3 import Row, connect

from models import SQLTableWithHeaders


def query_sqlite(sql: str, db_path: Path) -> list[Row]:
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    with connect(db_path.as_posix()) as conn:
        conn.row_factory = Row
        cur = conn.execute(sql)
        return cur.fetchall()



def get_sqlite_tables(db_path: Path) -> str:
    with connect(db_path.as_posix()) as conn:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        ]
        # TODO
        return reduce(
            lambda acc, t: f"{acc}\n{t}",
            [
                SQLTableWithHeaders(
                    table,
                    [col[1] for col in conn.execute(f"PRAGMA table_info({table});")],
                )
                for table in tables
            ],
            "",
        )

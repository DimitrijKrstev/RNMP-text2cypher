from pathlib import Path
from sqlite3 import Row, connect

from database.constants import SQLITE_DB_PATH
from models import SQLTableWithHeaders


def get_sqlite_tables() -> list[SQLTableWithHeaders]:
    with connect(SQLITE_DB_PATH) as conn:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        ]
        return [
            SQLTableWithHeaders(
                table, [col[1] for col in conn.execute(f"PRAGMA table_info({table});")]
            )
            for table in tables
        ]


def query_sqlite(sql: str) -> list[Row]:
    db_path = Path(SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect(db_path.as_posix()) as conn:
        conn.row_factory = Row
        cur = conn.execute(sql)
        return cur.fetchall()

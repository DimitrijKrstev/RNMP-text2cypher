from pathlib import Path
import duckdb

from database.constants import DUCKDB_PATH
from models import SQLTableWithHeaders


def query_duckdb(sql: str, db_path: str):
    conn = duckdb.connect(str(db_path))
    conn.execute("USE relbench.main")
    return conn.execute(sql).fetchall()


def get_duckdb_tables() -> str:
    conn = duckdb.connect(str(DUCKDB_PATH))
    tables = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
    
    result = ""
    for table in tables:
        columns = [row[0] for row in conn.execute(f"DESCRIBE {table}").fetchall()]
        result += f"\n{SQLTableWithHeaders(table, columns)}"
    
    return result
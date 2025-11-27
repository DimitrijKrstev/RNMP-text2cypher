import sys
from pathlib import Path
import duckdb
import json
from constants import DUCKDB_PATH

sys.path.append(str(Path(__file__).resolve().parent.parent))
from models import SQLTableWithHeaders


def query_duckdb(sql: str, db_path: str):
    conn = duckdb.connect(str(db_path))
    conn.execute("USE relbench.main")
    return conn.execute(sql).fetchall()

def minimal_schema(database: str = 'rel-f1') -> dict:
    conn = duckdb.connect(str(DUCKDB_PATH.parent / database / 'relbench.duckdb'))

    tables = [t[0] for t in conn.execute("PRAGMA show_tables;").fetchall()]
    table_set = set(tables)
    
    schema_lines = []

    for table in tables:
        columns_info = conn.execute(f"PRAGMA table_info('{table}');").fetchall()
        columns = [f"{col[1]} ({col[2]})" for col in columns_info]
        pks = [col[1] for col in columns_info if col[5]]

        fks = []
        for col in columns_info:
            col_name = col[1]
            for suffix in ("Id", "_id"):
                if col_name.endswith(suffix) and col_name != table + suffix:
                    ref_table = col_name[:-len(suffix)]
                    if ref_table in table_set:
                        fks.append(f"{col_name} -> {ref_table}.{col_name}")
                    elif ref_table + "s" in table_set:
                        fks.append(f"{col_name} -> {ref_table}s.{col_name}")
                    break

        combined = columns + [f"PK: {pk}" for pk in pks] + [f"FK: {fk}" for fk in fks]
        schema_lines.append(f"{table}: {', '.join(combined)}")

    conn.close()
    return schema_lines

if __name__ == '__main__':
    minimal_schema()

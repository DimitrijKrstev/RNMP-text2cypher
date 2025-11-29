import sys
from pathlib import Path
import duckdb
import json
from database.constants import DUCKDB_PATH
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

def json_schema_generator(database: str = 'rel-f1') -> dict:
    output_dir = DUCKDB_PATH.parent / database / 'relbench.duckdb'
    conn = duckdb.connect(str(output_dir))

    tables = [t[0] for t in conn.execute("PRAGMA show_tables;").fetchall()]
    table_set = set(tables)
    
    schema = {}

    for table in tables:
        columns_info = conn.execute(f"PRAGMA table_info('{table}');").fetchall()
        
        schema[table] = {
            "columns": [{"name": col[1], "type": col[2]} for col in columns_info],
            "primary_keys": [col[1] for col in columns_info if col[5]],
            "foreign_keys": [
                {"column": col[1], "references": f"{ref}.{col[1]}"}
                for col in columns_info
                for suffix in ("Id", "_id")
                if col[1].endswith(suffix) and col[1] != table + suffix
                for ref in [col[1][:-len(suffix)]]
                if ref in table_set or f"{ref}s" in table_set
                for ref in [ref if ref in table_set else f"{ref}s"]
            ]
        }

    conn.close()

    output_dir = output_dir.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"_schema.json"
    
    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)

    return schema




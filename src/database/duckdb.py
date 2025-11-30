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

import re


def get_duckdb_schema(database: str = 'rel-f1', format: bool = False) -> dict | str:
    conn = duckdb.connect(str(DUCKDB_PATH.parent / database / 'relbench.duckdb'))

    tables = [t[0] for t in conn.execute("PRAGMA show_tables;").fetchall()]
    fk_map = {}
    fk_results = conn.execute("""
        SELECT table_name, constraint_text 
        FROM duckdb_constraints() 
        WHERE constraint_type = 'FOREIGN KEY'
    """).fetchall()
    
    for table_name, constraint_text in fk_results:
        # Parse: "FOREIGN KEY (colName) REFERENCES refTable(refCol)"
        match = re.match(r'FOREIGN KEY \((\w+)\) REFERENCES (\w+)\(', constraint_text)
        if match:
            fk_col, ref_table = match.groups()
            fk_map[(table_name, fk_col)] = ref_table
    
    schema_lines = []

    for table in tables:
        columns_info = conn.execute(f"PRAGMA table_info('{table}');").fetchall()
        
        column_parts = []
        for col in columns_info:
            col_name, col_type, is_pk = col[1], col[2], col[5]
            
            markers = []
            if is_pk:
                markers.append("PK")
            if (table, col_name) in fk_map:
                markers.append(f"FK -> {fk_map[(table, col_name)]}")
            
            if markers:
                column_parts.append(f"{col_name} ({col_type}, {', '.join(markers)})")
            else:
                column_parts.append(f"{col_name} ({col_type})")

        schema_lines.append(f"Table name: {table} | Columns: {', '.join(column_parts)}")

    conn.close()
    
    if format:
        return "\n".join(schema_lines)

    return schema_lines



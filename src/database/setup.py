from logging import getLogger
from os import makedirs
import duckdb
from pathlib import Path
import pandas as pd
from graphlib import TopologicalSorter



from relbench.datasets import get_dataset

from database.constants import CSV_OUTPUT_DIR, DUCKDB_PATH

logger = getLogger(__name__)


def get_node_csvs(dataset_name: str, sample_fraction: float) -> None:
    dataset = get_dataset(name=dataset_name, download=True)
    db = dataset.get_db()

    tables = list(db.table_dict.keys())
    logger.info(f"Available tables: {tables}")

    sampled_nct_ids = None
    
    if sample_fraction < 1.0 and 'studies' in db.table_dict:
        sampled_studies = db.table_dict['studies'].df.sample(frac=sample_fraction, random_state=42)
        sampled_nct_ids = set(sampled_studies['nct_id'].values)

    csv_output_dir_name = CSV_OUTPUT_DIR / dataset_name
    makedirs(csv_output_dir_name, exist_ok=True)

    for table_name in tables:
        table_df = db.table_dict[table_name].df.copy()

        if sampled_nct_ids and 'nct_id' in table_df.columns:
            table_df = table_df[table_df['nct_id'].isin(sampled_nct_ids)]

        table_df.rename(
            columns={table_df.columns[0]: f"{table_df.columns[0]}:ID({table_name}-ID)"},
            inplace=True,
        )
        table_df[":LABEL"] = table_name

        table_df.to_csv(csv_output_dir_name / f"{table_name}_nodes.csv", index=False)

        logger.info(f"Wrote {table_name}_nodes.csv with {len(table_df)} rows.")


def load_ddl_schema(conn: duckdb.DuckDBPyConnection, ddl_path: Path) -> None:
    """Load and execute DDL schema to create tables."""
    ddl_sql = ddl_path.read_text()
    conn.execute(ddl_sql)
    logger.info(f"Schema loaded from: {ddl_path}")


def insert_table_data(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Insert dataframe into an existing table."""
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM dataframe")
    logger.info(f"Inserted {len(dataframe)} rows into {table_name}")


def get_insertion_order(database) -> list[str]:
    """Return table names sorted by foreign key dependencies (parents first)."""
    graph = {}
    for table_name, tbl in database.table_dict.items():
        fk_deps = getattr(tbl, 'fkey_col_to_pkey_table', {})
        graph[table_name] = set(fk_deps.values())
    
    sorter = TopologicalSorter(graph)
    return list(sorter.static_order())


def load_dataset_to_duckdb(
    dataset_name: str,
    sample_fraction: float = 1.0
) -> None:
    """Load dataset into DuckDB using a predefined DDL schema."""
    
    dataset = get_dataset(name=dataset_name, download=True)
    database = dataset.get_db()
    
    sampled_nct_ids = None
    if sample_fraction < 1.0 and 'studies' in database.table_dict:
        sampled_studies = database.table_dict['studies'].df.sample(
            frac=sample_fraction, random_state=42
        )
        sampled_nct_ids = set(sampled_studies['nct_id'].values)

    duckdb_dir = DUCKDB_PATH.parent / dataset_name
    duckdb_dir.mkdir(parents=True, exist_ok=True)
    db_path = duckdb_dir / "relbench.duckdb"
    ddl_path = duckdb_dir / "DDL.sql"
    conn = duckdb.connect(str(db_path))
    
    try:
        load_ddl_schema(conn, ddl_path)
        
        for table_name in get_insertion_order(database):
            tbl = database.table_dict.get(table_name)
            if tbl is None:
                continue
                
            dataframe = getattr(tbl, "df", None)
            if dataframe is None:
                logger.warning(f"Skipping {table_name}: no dataframe found")
                continue

            if sampled_nct_ids and 'nct_id' in dataframe.columns:
                dataframe = dataframe[dataframe['nct_id'].isin(sampled_nct_ids)]
            
            insert_table_data(conn, table_name, dataframe)

        logger.info(f"Done. DuckDB at: {db_path.resolve()}")
    finally:
        conn.close()
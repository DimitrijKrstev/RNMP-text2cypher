import os
from logging import getLogger
from sqlite3 import connect

from relbench.datasets import get_dataset

from database.constants import CSV_OUTPUT_DIR
from database.sqlite import SQLITE_DB_PATH

logger = getLogger(__name__)


def get_node_csvs(dataset_name: str) -> None:
    dataset = get_dataset(name=dataset_name, download=True)
    db = dataset.get_db()

    tables = list(db.table_dict.keys())
    logger.info(f"Available tables: {tables}")

    csv_output_dir_name = CSV_OUTPUT_DIR / dataset_name
    os.makedirs(csv_output_dir_name, exist_ok=True)

    for table_name in tables:
        table_df = db.table_dict[table_name].df.copy()

        table_df.rename(
            columns={table_df.columns[0]: f"{table_df.columns[0]}:ID({table_name}-ID)"},
            inplace=True,
        )
        table_df[":LABEL"] = table_name

        table_df.to_csv(csv_output_dir_name / f"{table_name}_nodes.csv", index=False)

        logger.info(f"Wrote {table_name}_nodes.csv with {len(table_df)} rows.")


def load_dataset_to_sqlite(dataset_name: str) -> None:
    dataset = get_dataset(name=dataset_name, download=True)
    database = dataset.get_db()

    sql_database_dir = SQLITE_DB_PATH.parent / dataset_name
    sql_database_dir.mkdir(parents=True, exist_ok=True)

    db_path = sql_database_dir / "relbench.db"

    con = connect(db_path.as_posix())
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")

        for name, tbl in database.table_dict.items():
            dataframe = getattr(tbl, "df", None)
            if dataframe is None:
                print(f"Skipping {name}: no dataframe found")
                continue

            print(f"Writing {name} ({len(dataframe)} rows)…")
            dataframe.to_sql(name, con, if_exists="replace", index=False)

        con.commit()
        logger.info(f"Done. SQLite DB at: {db_path.resolve()}")
    except Exception as e:
        logger.error(f"Error saving dataset to SQLite: {e}")
    finally:
        con.close()

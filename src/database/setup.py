import os
from logging import getLogger
from sqlite3 import connect

from relbench.datasets import get_dataset

from database.constants import CSV_OUTPUT_DIR
from database.sqlite import SQLITE_DB_PATH

logger = getLogger(__name__)


def get_node_csvs() -> None:
    dataset = get_dataset(name="rel-f1", download=True)
    db = dataset.get_db()

    tables = list(db.table_dict.keys())
    logger.info(f"Available tables: {tables}")

    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

    for table_name in tables:
        table_df = db.table_dict[table_name].df.copy()

        table_df.rename(
            columns={table_df.columns[0]: f"{table_df.columns[0]}:ID({table_name}-ID)"},
            inplace=True,
        )
        table_df[":LABEL"] = table_name

        table_df.to_csv(
            os.path.join(CSV_OUTPUT_DIR, f"{table_name}_nodes.csv"), index=False
        )


def load_dataset_to_sqlite():
    dataset = get_dataset(name="rel-f1", download=True)
    database = dataset.get_db()

    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = connect(SQLITE_DB_PATH.as_posix())
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
        logger.info(f"Done. SQLite DB at: {SQLITE_DB_PATH.resolve()}")
    except Exception as e:
        logger.error(f"Error saving dataset to SQLite: {e}")
    finally:
        con.close()

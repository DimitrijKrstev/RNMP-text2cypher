import sqlite3

from constants import SQLITE_DB_PATH
from relbench.datasets import get_dataset


def main():
    ds = get_dataset(name="rel-f1", download=True)
    db = ds.get_db()

    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(SQLITE_DB_PATH.as_posix())
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")

        for name, tbl in db.table_dict.items():
            df = getattr(tbl, "df", None)
            if df is None:
                print(f"Skipping {name}: no dataframe found")
                continue
            print(f"Writing {name} ({len(df)} rows)…")
            df.to_sql(name, con, if_exists="replace", index=False)

        con.commit()
    finally:
        con.close()

    print(f"Done. SQLite DB at: {SQLITE_DB_PATH.resolve()}")


if __name__ == "__main__":
    main()

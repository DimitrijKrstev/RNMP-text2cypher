import os

from relbench.datasets import get_dataset

from constants import CSV_OUTPUT_DIR


def main() -> None:
    dataset = get_dataset(name="rel-f1", download=True)
    db = dataset.get_db()

    tables = list(db.table_dict.keys())
    print(f"Available tables: {tables}")

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


if __name__ == "__main__":
    main()

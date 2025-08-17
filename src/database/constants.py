from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SQLITE_DB_PATH = PROJECT_ROOT / "sqlite" / "relbench.db"
CSV_OUTPUT_DIR = PROJECT_ROOT / "neo4j" / "import"

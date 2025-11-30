from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DUCKDB_PATH = PROJECT_ROOT / "duckdb" / "relbench.duckdb"

CSV_OUTPUT_DIR = PROJECT_ROOT / "neo4j" / "import"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"

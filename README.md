# RNMP Text2Cypher

Benchmark framework comparing Text-to-SQL vs Text-to-Cypher performance using [RelBench](https://relbench.stanford.edu/) datasets.

## What It Does

Evaluates LLM ability to convert natural language into:
- **SQL** queries (SQLite/DuckDB)
- **Cypher** queries (Neo4j graph database)

Measures: syntactic correctness, result accuracy, and exact query matching across easy/intermediate/hard difficulty levels.

## Datasets

- **rel-f1**: Formula 1 data (1950-2024) - circuits, drivers, constructors, races, results, standings
- **rel-stack**: Stack Overflow data - posts, users, comments, votes, badges, post history

## Setup

```bash
# Install dependencies
uv sync
source .venv/bin/activate

# Configure environment (required for remote evaluation)
cp .env.sample .env
# Edit .env and add:
# OPENAI_API_KEY=your_key_here  (for remote models)
# HF_TOKEN=your_token_here       (optional, for some HuggingFace models)
```

## Prepare Data

### Choose Your SQL Database

**Option 1: DuckDB** (recommended - faster for analytical queries)
```bash
uv run src/main.py load-duckdb --dataset-name rel-f1
```

**Option 2: SQLite** (alternative)
```bash
uv run src/main.py load-sqlite --dataset-name rel-f1
```

**Note**: The evaluation uses DuckDB by default. To switch, edit `src/evaluation/scoring.py` and change `query_duckdb` to `query_sqlite`.

### Setup Neo4j (for Cypher evaluation)

```bash
# Generate CSVs for Neo4j import
uv run src/main.py generate-csvs --dataset-name rel-f1

# Start Neo4j container
cd neo4j/
DATASET_NAME=rel-f1 docker compose up -d --build

# Access at http://localhost:7474 (username: neo4j, password: neo4jneo4j)
```

**Switching datasets**: Only one dataset can be active at a time. To switch:
```bash
docker compose down -v
DATASET_NAME=rel-stack docker compose up -d --build
```

## Run Evaluations

### Validate Tasks First
```bash
uv run src/main.py validate-tasks --dataset-name rel-f1
```

### Evaluate Models
```bash
# Local model (requires GPU for optimal performance)
uv run src/main.py evaluate-local --dataset-name rel-f1 --task-types SQL --task-types CYPHER

# Remote model (requires OPENAI_API_KEY in .env)
uv run src/main.py evaluate-remote --dataset-name rel-f1 --task-types SQL --task-types CYPHER

# Re-evaluate existing results (useful for testing scoring changes)
uv run src/main.py re-evaluate-results --dataset-name rel-f1 --task-type SQL

# Generate visualizations
uv run src/main.py plot-evaluation-results --dataset-name rel-f1
```

## All Available Commands

```bash
# Data preparation
uv run src/main.py generate-csvs --dataset-name {rel-f1|rel-stack}
uv run src/main.py load-sqlite --dataset-name {rel-f1|rel-stack}   # Option 1
uv run src/main.py load-duckdb --dataset-name {rel-f1|rel-stack}   # Option 2 (default)

# Utilities
uv run src/main.py get-neo4j                                        # Print Neo4j schema
uv run src/main.py validate-tasks --dataset-name {rel-f1|rel-stack}

# Evaluation
uv run src/main.py evaluate-local --dataset-name {rel-f1|rel-stack} --task-types {SQL|CYPHER} [--task-types ...]
uv run src/main.py evaluate-remote --dataset-name {rel-f1|rel-stack} --task-types {SQL|CYPHER} [--task-types ...]

# Re-evaluation & Analysis
uv run src/main.py re-evaluate-results --dataset-name {rel-f1|rel-stack} --task-type {SQL|CYPHER}
uv run src/main.py plot-evaluation-results --dataset-name {rel-f1|rel-stack}
```

## Results

**Location**: `src/results/<dataset>/<task-type>/<model>/<difficulty>.json`

Each result includes:
```json
{
  "question": "Natural language question",
  "expected_script": "Ground truth query",
  "generated_script": "Model-generated query",
  "syntaxically_correct": true,  // Query executes without errors
  "correct_result": true,        // Returns same results as ground truth
  "exact_match": false           // Exactly matches ground truth (normalized)
}
```

**Plots**: `src/plots/<dataset>/` - Bar charts showing performance metrics by difficulty

### Database Connections
Edit `src/database/constants.py`:
```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"
```

### Project Structure
```
src/
├── database/       # Database connections (neo4j.py, sqlite.py, duckdb.py, setup.py)
├── evaluation/     # Evaluation framework (local_eval.py, remote_eval.py, scoring.py, plot.py)
├── tasks/          # Benchmark tasks (rel-f1/, rel-stack/)
├── results/        # Generated evaluation results
├── plots/          # Generated visualizations
├── constants.py    # Configuration
├── models.py       # Data models
├── utils.py        # Helpers
└── main.py         # CLI entry point

neo4j/
├── scripts/        # Setup scripts (constraints/, relationships/, verify-scripts/)
├── import/         # Generated CSV data
└── Dockerfile      # Container configuration
```

## Requirements

- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** - Package manager
- **Docker** - For Neo4j


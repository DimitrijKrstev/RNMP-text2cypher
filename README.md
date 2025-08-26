# RNMP text2cypher

## Setup

This project uses [uv](https://github.com/astral-sh/uv) as a package manager and is a prerequisite for this project. Using uv, to install this project's dependencies do:

```bash
uv sync
```

You can then source the interperter by doing:

```bash
source .venv/bin/activate
```

Additionally [docker](https://www.docker.com/) is required to run the database.

## Running neo4j populated

In order for the [relbench f1 database](https://relbench.stanford.edu/datasets/rel-f1/) to be loaded into neo4j it is first downloaded locally and converted to a csv format. To do so, run the following:

```bash
uv run src/database/get_node_csvs.py
```

This will download the relbench f1 database locally and then convert all required entities into node csv files.

To run the neo4j database simply run the docker compose located inside the `/neo4j` folder:

```bash
cd neo4j/
docker compose up -d --build
```

This will import the nodes via the `import-nodes.sh` script and will add the required constraints and relationships via the `import-relationships.sh` script inside the `scripts/` directory.

### Accessing remote interface

To access the remote interface of the neo4j database simply navigate to `http://localhost:7474/` on you browser. You can run queries here and analyze the data. 

## Populating SQLite

In order to populate [SQLite](https://sqlite.org/) locally, run:

```bash
uv run src/database/save_to_sqlite.py
```

### Verifying Database Integrity

To verify that all relationships were created correctly and check data quality:

```bash
cd neo4j/
./scripts/run-verification.sh
```

This will run comprehensive checks on:
- Node and relationship counts
- Orphaned nodes
- Data consistency
- Sample relationship paths

## Dev tools

Before contributing make sure to run the following dev tools and fix issues related with the following:

```
isort .
flake8
mypy .
black .
```

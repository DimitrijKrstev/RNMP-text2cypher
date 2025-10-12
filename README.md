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
uv run src/main.py generate-csvs --dataset-name <dataset_name>
```
Replace `<dataset_name>` with either `rel-f1` or `rel-stack` (e.g., `--dataset-name rel-f1`).

This will download the relbench f1 or stack database locally and then convert all required entities into node csv files.

To run the neo4j database simply run the docker compose located inside the `/neo4j` folder, with the specified db after you have previous ran it's respective download csv's command:

Run one of these rel-f1 or rel-stack depending on which db you want to initialize

```bash
cd neo4j/
DATASET_NAME=<dataset_name> docker compose up -d --build
```

This will import the nodes via the `import-nodes.sh` script and will add the required constraints and relationships via the `import-relationships.sh` script inside the `scripts/` directory.

### Accessing remote interface

To access the remote interface of the neo4j database simply navigate to `http://localhost:7474/` on you browser. You can run queries here and analyze the data. 

## Populating SQLite

In order to populate [SQLite](https://sqlite.org/) locally, run:

```bash
uv run src/main.py load-sqlite --dataset-name <dataset_name>
```

## Relationship Schema

### Node Types
- `circuits`: F1 racing circuits
- `drivers`: F1 drivers
- `constructors`: F1 teams/constructors
- `races`: Individual race events
- `results`: Race results
- `qualifying`: Qualifying session results
- `standings`: Driver championship standings
- `constructor_results`: Constructor race results
- `constructor_standings`: Constructor championship standings

### Relationships
- `drivers -[ACHIEVED]-> results`
- `constructors -[ACHIEVED]-> results`
- `races -[HELD_AT]-> circuits`
- `results -[IN_RACE]-> races`
- `drivers -[QUALIFIED_IN]-> qualifying`
- `constructors -[QUALIFIED_IN]-> qualifying`
- `qualifying -[FOR_RACE]-> races`
- `races -[IN_STANDING]-> standings`
- `drivers -[ACHIEVED_STANDING]-> standings`
- `races -[RESULTED_IN]-> constructor_results`
- `constructors -[RESULTED_IN]-> constructor_results`
- `races -[HAS_STANDING]-> constructor_standings`
- `constructors -[HAS_STANDING]-> constructor_standings`

### Verifying Database Integrity

Scripts for verification on relationship types as well as data integrity are run automatically on startup. 
To see their results check the container log.

The scripts will run comprehensive checks on:
- Node and relationship counts
- Orphaned nodes
- Data consistency
- Sample relationship paths etc.

## Dev tools

Before contributing make sure to run the following dev tools and fix issues related with the following:

```
isort .
flake8
mypy .
black .
```

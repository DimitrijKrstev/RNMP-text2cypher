# RNMP text2cypher

## Setup

This project uses [uv](https://github.com/astral-sh/uv) as a package manager and is a prerequisite for this project. Using uv, to install this project's dependencies do:

```bash
uv sync
```

Additionally [docker](https://www.docker.com/) is required to run the database.

## Running neo4j populated

In order for the [relbench f1 database](https://relbench.stanford.edu/datasets/rel-f1/) to be loaded into neo4j it is first downloaded locally and converted to a csv format. To do so, run the following:

```bash
uv run get_node_csvs.py
```

This will install the relbench f1 database locally and then convert all required entities into node csv files.

To run the neo4j database simply run the docker compose:

```bash
docker compose up -d --build
```

This will import the nodes via the `import-nodes.sh` script and will add the required constraints and relationships via the `f1-database-loader.sh` script.

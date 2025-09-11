from functools import reduce
from typing import Any

from neo4j import GraphDatabase

from database.constants import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def query_neo4j(cypher: str, parameters: dict | None = None) -> list[dict[str, Any]]:
    with _driver.session() as session:
        result = session.run(cypher, parameters or {})
        return [record.data() for record in result]


def get_neo4j_schema() -> str:
    with _driver.session() as session:
        labels = [
            record["label"] for record in session.run("CALL db.labels() YIELD label")
        ]

        nodes = []
        for label in labels:
            properties = [
                key
                for record in session.run(
                    f"MATCH (n:`{label}`) UNWIND keys(n) AS key RETURN DISTINCT key"
                )
                for key in record.values()
            ]
            nodes.append({"label": label, "properties": properties})

        relationships = []
        result = session.run(
            """
            MATCH (a)-[r]->(b)
            RETURN type(r) AS rel,
                   collect(DISTINCT labels(a)) AS from_labels,
                   collect(DISTINCT labels(b)) AS to_labels,
                   collect(DISTINCT keys(r)) AS props
            """
        )
        for record in result:
            relationships.append(
                {
                    "name": record["rel"],
                    "start_labels": list(
                        {label for sub in record["from_labels"] for label in sub}
                    ),
                    "end_labels": list(
                        {label for sub in record["to_labels"] for label in sub}
                    ),
                    "properties": list(
                        {property for sub in record["props"] for property in sub}
                    ),
                }
            )

        nodes = reduce(
            lambda acc, node: f"{acc}\nNode: {node['label']}({', '.join(node['properties'])})",
            nodes,
            "",
        )
        relationships = reduce(
            lambda acc, rel: f"{acc}\nRelationship: {','.join(rel['start_labels'])} -[{rel['name']}({', '.join(rel['properties'])})]-> {','.join(rel['end_labels'])}",
            relationships,
            "",
        )

        return f"{nodes}\n\n{relationships}"

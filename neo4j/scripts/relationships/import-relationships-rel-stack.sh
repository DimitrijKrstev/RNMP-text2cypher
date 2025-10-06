#!/usr/bin/env bash
set -euo pipefail

BATCH=10000
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

run() {
    cypher-shell -u "$USER" -p "$PASS" --non-interactive "$1"
}

echo "------ Building relationships in batches of $BATCH ------"

run "
CALL {
    MATCH (pl:postLinks) MATCH (p:posts)
    WHERE p.Id = pl.PostId
    MERGE (p)-[:LINK_TO]->(pl)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (pl:postLinks) MATCH (p:posts)
    WHERE p.Id = pl.RelatedPostId
    MERGE (p)-[:LINK_TO]->(pl)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (c:comments) MATCH (p:posts)
    WHERE p.Id = c.PostId
    MERGE (c)-[:COMMENTS_ON]->(p)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (c:comments) MATCH (u:users)
    WHERE u.Id = c.UserId
    MERGE (u)-[:WROTE]->(c)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (ph:postHistory) MATCH (u:users)
    WHERE ph.UserId = u.Id
    MERGE (ph)-[:WAS_WRITTEN_BY]->(u)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (ph:postHistory) MATCH (p:posts)
    WHERE ph.PostId = p.Id
    MERGE (ph)-[:RELATES_TO]->(p)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (b:badges) MATCH (u:users)
    WHERE b.UserId = u.Id
    MERGE (b)-[:BELONG_TO]->(u)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (v:votes) MATCH (u:users)
    WHERE v.UserId = u.Id
    MERGE (v)-[:VOTED_BY]->(u)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (v:votes) MATCH (p:posts)
    WHERE v.PostId = p.Id
    MERGE (v)-[:VOTED_ON]->(p)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (p:posts) MATCH (u:users)
    WHERE p.OwnerUserId = u.Id
    MERGE (u)-[:OWNS]->(p)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (parent:posts) MATCH (child:posts)
    WHERE child.ParentId = parent.Id
    MERGE (parent)-[:HAS_ANSWER]->(child)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
    MATCH (question:posts) MATCH (answer:posts)
    WHERE question.AcceptedAnswerId = answer.Id
    MERGE (question)-[:ACCEPTED_ANSWER]->(answer)
} IN TRANSACTIONS OF $BATCH ROWS;
"

echo "------ Relationship import finished ------"
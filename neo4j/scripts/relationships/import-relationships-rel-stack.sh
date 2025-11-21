#!/usr/bin/env bash
set -euo pipefail

BATCH=1000
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

run() {
    cypher-shell -u "$USER" -p "$PASS" --non-interactive "$1"
}

run "
  CALL {
    MATCH (p:posts), (pl:postLinks)
    WHERE p.Id = pl.PostId
    MERGE (p)-[:HAS_LINK]->(pl)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (pl:postLinks), (p:posts)
    WHERE p.Id = pl.RelatedPostId
    MERGE (pl)-[:POINTS_TO]->(p)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (c:comments), (p:posts)
    WHERE p.Id = c.PostId
    MERGE (c)-[:IS_ON]->(p)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (u:users), (c:comments)
    WHERE u.Id = c.UserId
    MERGE (u)-[:WROTE]->(c)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (u:users), (ph:postHistory)
    WHERE ph.UserId = u.Id
    MERGE (u)-[:EDITED]->(ph)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (ph:postHistory), (p:posts)
    WHERE ph.PostId = p.Id
    MERGE (ph)-[:RELATES_TO]->(p)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (u:users), (b:badges)
    WHERE b.UserId = u.Id
    MERGE (u)-[:EARNED]->(b)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (u:users), (v:votes)
    WHERE v.UserId = u.Id
    MERGE (u)-[:CAST]->(v)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (v:votes), (p:posts)
    WHERE v.PostId = p.Id
    MERGE (v)-[:VOTED_ON]->(p)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (u:users), (p:posts)
    WHERE p.OwnerUserId = u.Id
    MERGE (u)-[:OWNS]->(p)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (parent:posts), (child:posts)
    WHERE child.ParentId = parent.Id
    MERGE (parent)-[:HAS_ANSWER]->(child)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

run "
  CALL {
    MATCH (question:posts), (answer:posts)
    WHERE question.AcceptedAnswerId = answer.Id
    MERGE (question)-[:ACCEPTED_ANSWER]->(answer)
  } IN TRANSACTIONS OF $BATCH ROWS;
"

echo "------ Relationship import finished ------"
#!/usr/bin/env bash
set -euo pipefail

BATCH=10000
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

run() {
    cypher-shell -u "$USER" -p "$PASS" --non-interactive "$1"
}


run "
  MATCH (pl:postLinks) MATCH (p:posts)
  WHERE p.Id = pl.PostId
  MERGE (p)-[:LINK_TO]->(pl);
"

run "
  MATCH (pl:postLinks) MATCH (p:posts)
  WHERE p.Id = pl.RelatedPostId
  MERGE (p)-[:LINK_TO]->(pl);
"
run "
  MATCH (c:comments) MATCH (p:posts)
  WHERE p.Id = c.PostId
  MERGE (c)-[:COMMENTS_ON]->(p);
"

run "
  MATCH (c:comments) MATCH (u:users)
  WHERE u.Id = c.UserId
  MERGE (u)-[:WROTE]->(c);
"

run "
  MATCH (ph:postHistory) MATCH (u:users)
  WHERE ph.UserId = u.Id
  MERGE (ph)-[:WAS_WRITTEN_BY]->(u);
"

run "
  MATCH (ph:postHistory) MATCH (p:posts)
  WHERE ph.PostId = p.Id
  MERGE (ph)-[:RELATES_TO]->(p);
"

run "
  MATCH (b:badges) MATCH (u:users)
  WHERE b.UserId = u.Id
  MERGE (b)-[:BELONG_TO]->(u);
"

run "
  MATCH (v:votes) MATCH (u:users)
  WHERE v.UserId = u.Id
  MERGE (v)-[:VOTED_BY]->(u);
"

run "
  MATCH (v:votes) MATCH (p:posts)
  WHERE v.PostId = p.Id
  MERGE (v)-[:VOTED_ON]->(p);
"

run "
  MATCH (p:posts) MATCH (u:users)
  WHERE p.OwnerUserId = u.Id
  MERGE (u)-[:OWNS]->(p);
"

run "
  MATCH (parent:posts) MATCH (child:posts)
  WHERE child.ParentId = parent.Id
  MERGE (parent)-[:HAS_ANSWER]->(child);
"

run "
  MATCH (question:posts) MATCH (answer:posts)
  WHERE question.AcceptedAnswerId = answer.Id
  MERGE (question)-[:ACCEPTED_ANSWER]->(answer);
"

echo "------ Relationship import finished ------"
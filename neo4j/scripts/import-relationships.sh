#!/usr/bin/env bash
set -euo pipefail
BATCH=1000
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

run() {
  cypher-shell -u "$USER" -p "$PASS" --non-interactive "$1"
}

echo "------ Building relationships in batches of $BATCH ------"

run "
CALL {
  MATCH (d:drivers)   MATCH (r:results)
  WHERE r.driverId = d.driverId
  MERGE (d)-[:ACHIEVED]->(r)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (c:constructors) MATCH (r:results)
  WHERE r.constructorId = c.constructorId
  MERGE (c)-[:ACHIEVED]->(r)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (ra:races) MATCH (ci:circuits)
  WHERE coalesce(ra.circuitId, ra.circutId) = ci.circuitId
  MERGE (ra)-[:HELD_AT]->(ci)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (r:results) MATCH (ra:races)
  WHERE r.raceId = ra.raceId
  MERGE (r)-[:IN_RACE]->(ra)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (d:drivers) MATCH (q:qualifying)
  WHERE q.driverId = d.driverId
  MERGE (d)-[:QUALIFIED_IN]->(q)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (c:constructors) MATCH (q:qualifying)
  WHERE q.constructorId = c.constructorId
  MERGE (c)-[:QUALIFIED_IN]->(q)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (q:qualifying) MATCH (ra:races)
  WHERE q.raceId = ra.raceId
  MERGE (q)-[:FOR_RACE]->(ra)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (ra:races) MATCH (s:standings)
  WHERE s.raceId = ra.raceId
  MERGE (ra)-[:IN_STANDING]->(s)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (d:drivers) MATCH (s:standings)
  WHERE s.driverId = d.driverId
  MERGE (d)-[:ACHIEVED_STANDING]->(s)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (ra:races) MATCH (cr:constructor_results)
  WHERE cr.raceId = ra.raceId
  MERGE (ra)-[:RESULTED_IN]->(cr)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (c:constructors) MATCH (cr:constructor_results)
  WHERE cr.constructorId = c.constructorId
  MERGE (c)-[:RESULTED_IN]->(cr)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (ra:races) MATCH (cs:constructor_standings)
  WHERE cs.raceId = ra.raceId
  MERGE (ra)-[:HAS_STANDING]->(cs)
} IN TRANSACTIONS OF $BATCH ROWS;

CALL {
  MATCH (c:constructors) MATCH (cs:constructor_standings)
  WHERE cs.constructorId = c.constructorId
  MERGE (c)-[:HAS_STANDING]->(cs)
} IN TRANSACTIONS OF $BATCH ROWS;
"

echo "------ Relationship import finished ------"
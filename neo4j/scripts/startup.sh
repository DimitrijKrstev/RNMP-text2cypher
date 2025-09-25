#!/usr/bin/env bash
# -----------------------------------------
#  One-shot set-up for the F1 knowledge-graph
# -----------------------------------------
set -euo pipefail

echo "DEBUG: Received argument: '$1'"
echo "DEBUG: All arguments: '$@'"

DATASET_NAME=${1:-${DATASET_NAME:-rel-f1}}
USER=neo4j
PASSWORD=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}
REL_SCRIPT=/var/lib/neo4j/scripts/relationships/import-relationships-${DATASET_NAME}.sh
CONSTRAINT_FILE=/var/lib/neo4j/scripts/constraints/create-constraints-${DATASET_NAME}.cypher
VERIFY_SCRIPT=/var/lib/neo4j/scripts/verify-scripts/run-verification.sh

DATASET_NAME=${1:-rel-f1}
echo "DEBUG: DATASET_NAME = '$DATASET_NAME'"
echo "DEBUG: Looking for constraint file: /var/lib/neo4j/scripts/constraints/create-constraints-${DATASET_NAME}.cypher"

CONSTRAINT_FILE=/var/lib/neo4j/scripts/constraints/create-constraints-${DATASET_NAME}.cypher
echo "DEBUG: CONSTRAINT_FILE = '$CONSTRAINT_FILE'"

# helper – wait until bolt is available
wait_for_neo4j () {
  echo "------ Waiting for Neo4j to start… ------"
  for i in {1..60}; do
    if cypher-shell -u "$USER" -p "$PASSWORD" 'RETURN 1' >/dev/null 2>&1; then
      echo "------ Neo4j is up ------"
      return
    fi
    sleep 2
  done
  echo "------ Neo4j did not become available in time ------" >&2
  exit 1
}

#  1 – start db in the background
/startup/docker-entrypoint.sh neo4j &
db_pid=$!

#  2 – wait & apply constraints

wait_for_neo4j
echo "------ Applying (idempotent) constraints & indexes… ------"
cypher-shell -u "$USER" -p "$PASSWORD" -f "$CONSTRAINT_FILE"
echo "   …done"

#  3 – build relationships
echo "------ Creating relationships… ------"
"$REL_SCRIPT"
echo "------   …done ------"

#  4 – verification
# echo "------ Running verification suite… ------"
# "$VERIFY_SCRIPT" "$DATASET_NAME"
# echo "------  …verification finished ------"


#  5 – keep container running
echo ""
echo "------ ${DATASET_NAME} graph ready! ------"
echo "   Open the web interface at \"http://localhost:7474/browser/preview/\""
echo "   Login: neo4j / $PASSWORD"
echo "-----------------------------"
echo ""
wait "$db_pid"     # forward logs & signals
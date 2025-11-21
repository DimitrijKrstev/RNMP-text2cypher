#!/usr/bin/env bash

set -euo pipefail


DATASET_NAME=${1:-${DATASET_NAME:-rel-f1}}
USER=neo4j
PASSWORD=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}
REL_SCRIPT=/var/lib/neo4j/scripts/relationships/import-relationships-${DATASET_NAME}.sh
CONSTRAINT_FILE=/var/lib/neo4j/scripts/constraints/create-constraints-${DATASET_NAME}.cypher
MARKER_FILE="/data/.import_complete_${DATASET_NAME}"


echo "DEBUG: DATASET_NAME = '$DATASET_NAME'"
echo "DEBUG: Looking for constraint file: /var/lib/neo4j/scripts/constraints/create-constraints-${DATASET_NAME}.cypher"
echo "DEBUG: CONSTRAINT_FILE = '$CONSTRAINT_FILE'"


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

/startup/docker-entrypoint.sh neo4j &
db_pid=$!


wait_for_neo4j

if [ -f "$MARKER_FILE" ]; then
  echo "------ Dataset '${DATASET_NAME}' loaded ------"
  echo ""
  echo "------ ${DATASET_NAME} graph ready! ------"
  echo "   Open the web interface at \"http://localhost:7474/browser/preview/\""
  echo "   Login: neo4j / $PASSWORD"
  echo "-----------------------------"
  echo ""
  wait "$db_pid"     
  exit 0
fi

echo "------ Applying (idempotent) constraints & indexes… ------"
cypher-shell -u "$USER" -p "$PASSWORD" -f "$CONSTRAINT_FILE"
echo "------  DONE ------"

echo "------ Creating relationships… ------"
"$REL_SCRIPT"
echo "------  DONE ------"

touch "$MARKER_FILE"


echo ""
echo "------ ${DATASET_NAME} graph ready! ------"
echo "   Open the web interface at \"http://localhost:7474/browser/preview/\""
echo "   Login: neo4j / $PASSWORD"
echo "-----------------------------"
echo ""
wait "$db_pid"     
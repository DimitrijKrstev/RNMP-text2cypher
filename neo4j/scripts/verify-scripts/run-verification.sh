#!/usr/bin/env bash
set -euo pipefail

DATASET_NAME=${1:-rel-f1}
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

echo "============================================="
echo "      F1 Knowledge-Graph Verification"
echo "      $(date)"
echo "============================================="

cypher-shell -u "$USER" -p "$PASS" -f /var/lib/neo4j/scripts/verify-scripts/verify-relationships-${DATASET_NAME}.cypher
cypher-shell -u "$USER" -p "$PASS" -f /var/lib/neo4j/scripts/verify-scripts/verify-data-quality-${DATASET_NAME}.cypher

echo "============================================="
echo "   ✔ All verification queries executed"
echo "============================================="
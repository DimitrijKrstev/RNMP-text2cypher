#!/usr/bin/env bash
set -euo pipefail
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

echo "============================================="
echo "      F1 Knowledge-Graph Verification"
echo "      $(date)"
echo "============================================="

cypher-shell -u "$USER" -p "$PASS" -f /var/lib/neo4j/scripts/verify-scripts/verify-relationships.cypher
cypher-shell -u "$USER" -p "$PASS" -f /var/lib/neo4j/scripts/verify-scripts/verify-data-quality.cypher

echo "============================================="
echo "   ✔ All verification queries executed"
echo "============================================="
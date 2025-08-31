#!/usr/bin/env bash
# -----------------------------------------
#  One-shot set-up for the F1 knowledge-graph
# -----------------------------------------
set -euo pipefail

USER=neo4j
PASSWORD=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}
REL_SCRIPT=/var/lib/neo4j/scripts/import-relationships.sh
CONSTRAINT_FILE=/var/lib/neo4j/scripts/create-constraints.cypher
VERIFY_SCRIPT=/var/lib/neo4j/scripts/verify-scripts/run-verification.sh

# helper – wait until bolt is available
wait_for_neo4j () {
  echo "⏳ Waiting for Neo4j to start…"
  for i in {1..60}; do
    if cypher-shell -u "$USER" -p "$PASSWORD" 'RETURN 1' >/dev/null 2>&1; then
      echo "✅ Neo4j is up"
      return
    fi
    sleep 2
  done
  echo "❌ Neo4j did not become available in time" >&2
  exit 1
}

#  1 – start db in the background
/startup/docker-entrypoint.sh neo4j &
db_pid=$!

#  2 – wait & apply constraints

wait_for_neo4j
echo "📐 Applying (idempotent) constraints & indexes…"
cypher-shell -u "$USER" -p "$PASSWORD" -f "$CONSTRAINT_FILE"
echo "   …done"

#  3 – build relationships
echo "🔗 Creating relationships…"
"$REL_SCRIPT"
echo "   …done"

#  4 – verification
echo "🔍 Running verification suite…"
"$VERIFY_SCRIPT"
echo "   …verification finished"


#  5 – keep container running
echo ""
echo "🎉 F1 graph ready!  →  $GUIDE_URL"
echo "   Open the web interface at "http://localhost:7474/browser/preview/"
echo "   Login: neo4j / $PASSWORD"
echo ""
wait "$db_pid"     # forward logs & signals
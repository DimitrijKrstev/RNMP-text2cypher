# #!/usr/bin/env bash
# set -euo pipefail

# PASSWORD=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

# wait_for_neo4j() {
#     echo "Waiting for Neo4j…"
#     for _ in {1..60}; do
#         if cypher-shell -u neo4j -p "$PASSWORD" "RETURN 1" >/dev/null 2>&1; then
#             echo "Neo4j is up"
#             return 0
#         fi
#         sleep 2
#     done
#     echo "Neo4j did not become available in time" >&2
#     exit 1
# }

# create_constraints() {
#     echo "Creating constraints…"
    
#   cypher-shell -u neo4j -p "$PASSWORD" <<'CYPHER'
#     CREATE CONSTRAINT circuits_id     IF NOT EXISTS FOR (n:circuits)     REQUIRE n.circuitId      IS UNIQUE;
#     CREATE CONSTRAINT constructors_id IF NOT EXISTS FOR (n:constructors) REQUIRE n.constructorId  IS UNIQUE;
#     CREATE CONSTRAINT drivers_id      IF NOT EXISTS FOR (n:drivers)      REQUIRE n.driverId       IS UNIQUE;
#     CREATE CONSTRAINT races_id        IF NOT EXISTS FOR (n:races)        REQUIRE n.raceId         IS UNIQUE;
#     CREATE CONSTRAINT results_id      IF NOT EXISTS FOR (n:results)      REQUIRE n.resultId       IS UNIQUE;
#     CREATE CONSTRAINT qualifying_id   IF NOT EXISTS FOR (n:qualifying)   REQUIRE n.qualifyId      IS UNIQUE;
# CYPHER
# }


# create_relationships() {
#     echo "Creating relationships…"
    
#   cypher-shell -u neo4j -p "$PASSWORD" <<'CYPHER'
#     CALL () {
#       MATCH (r:results)
#       MATCH (d:drivers)
#       WHERE toInteger(r.driverId) = toInteger(d.driverId)
#       MERGE (d)-[:ACHIEVED]->(r)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (r:results)
#       MATCH (c:constructors)
#       WHERE toInteger(r.constructorId) = toInteger(c.constructorId)
#       MERGE (c)-[:ACHIEVED]->(r)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (ra:races)
#       MATCH (ci:circuits)
#       WHERE toInteger(ra.circuitId) = toInteger(ci.circuitId)
#       MERGE (ra)-[:HELD_AT]->(ci)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (r:results)
#       MATCH (ra:races)
#       WHERE toInteger(r.raceId) = toInteger(ra.raceId)
#       MERGE (r)-[:IN_RACE]->(ra)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (q:qualifying)
#       MATCH (d:drivers)
#       WHERE toInteger(q.driverId) = toInteger(d.driverId)
#       MERGE (d)-[:QUALIFIED_IN]->(q)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (q:qualifying)
#       MATCH (c:constructors)
#       WHERE toInteger(q.constructorId) = toInteger(c.constructorId)
#       MERGE (c)-[:QUALIFIED_IN]->(q)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (q:qualifying)
#       MATCH (ra:races)
#       WHERE toInteger(q.raceId) = toInteger(ra.raceId)
#       MERGE (q)-[:FOR_RACE]->(ra)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (s:standings)
#       MATCH (ra:races)
#       WHERE toInteger(s.raceId) = toInteger(ra.raceId)
#       MERGE (ra)-[:IN_STANDING]->(s)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (s:standings)
#       MATCH (d:drivers)
#       WHERE toInteger(s.driverId) = toInteger(d.driverId)
#       MERGE (d)-[:ACHIEVED_STANDING]->(s)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (cs:constructor_results)
#       MATCH (ra:races)
#       WHERE toInteger(cs.raceId) = toInteger(ra.raceId)
#       MERGE (ra)-[:RESULTED_IN]->(cs)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (cs:constructor_results)
#       MATCH (c:constructors)
#       WHERE toInteger(cs.constructorId) = toInteger(c.constructorId)
#       MERGE (c)-[:RESULTED_IN]->(cs)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (cst:constructor_standings)
#       MATCH (ra:races)
#       WHERE toInteger(cst.raceId) = toInteger(ra.raceId)
#       MERGE (ra)-[:HAS_STANDING]->(cst)
#     } IN TRANSACTIONS OF 1000 ROWS;

#     CALL () {
#       MATCH (cst:constructor_standings)
#       MATCH (c:constructors)
#       WHERE toInteger(cst.constructorId) = toInteger(c.constructorId)
#       MERGE (c)-[:HAS_STANDING]->(cst)
#     } IN TRANSACTIONS OF 1000 ROWS;

# CYPHER
#     echo "Relationships created"
# }



# summary() {
#     echo "Summary:"
    
#     cypher-shell -u neo4j -p "$PASSWORD" --non-interactive \
#     "MATCH (n) RETURN labels(n)[0] AS NodeType, count(*) AS Count ORDER BY NodeType;"
    
#     cypher-shell -u neo4j -p "$PASSWORD" --non-interactive \
#     "MATCH ()-[r]->() RETURN type(r) AS RelType, count(*) AS Count ORDER BY RelType;"
    
# }


# main() {
#     /startup/docker-entrypoint.sh neo4j &
#     wait_for_neo4j
#     create_constraints
#     create_relationships
#     summary
    
#     echo "Setting up browser guides..."
#     echo ":play http://localhost:7474/guides/verification-guide.html" > /var/lib/neo4j/import/startup.cypher

#     echo -e "\nF1 Graph loaded!"
#     echo "http://localhost:7474  (neo4j / $PASSWORD)"
#     echo ""
#     echo "🔍 To run verification queries, execute in browser:"
#     echo ":play http://localhost:7474/guides/verification-guide.html"
# }

# main

#!/bin/sh
set -eu

PASSWORD=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

wait_for_neo4j() {
    echo "Waiting for Neo4j…"
    i=1
    while [ $i -le 60 ]; do
        echo "Attempt $i/60..."
        if cypher-shell -u neo4j -p "$PASSWORD" "RETURN 1" >/dev/null 2>&1; then
            echo "Neo4j is up"
            return 0
        fi
        sleep 2
        i=$((i + 1))
    done
    echo "Neo4j did not become available in time" >&2
    exit 1
}

create_constraints() {
    echo "Creating constraints…"
    
    cypher-shell -u neo4j -p "$PASSWORD" <<'CYPHER'
CREATE CONSTRAINT circuits_id     IF NOT EXISTS FOR (n:circuits)     REQUIRE n.circuitId      IS UNIQUE;
CREATE CONSTRAINT constructors_id IF NOT EXISTS FOR (n:constructors) REQUIRE n.constructorId  IS UNIQUE;
CREATE CONSTRAINT drivers_id      IF NOT EXISTS FOR (n:drivers)      REQUIRE n.driverId       IS UNIQUE;
CREATE CONSTRAINT races_id        IF NOT EXISTS FOR (n:races)        REQUIRE n.raceId         IS UNIQUE;
CREATE CONSTRAINT results_id      IF NOT EXISTS FOR (n:results)      REQUIRE n.resultId       IS UNIQUE;
CREATE CONSTRAINT qualifying_id   IF NOT EXISTS FOR (n:qualifying)   REQUIRE n.qualifyId      IS UNIQUE;
CYPHER
    
    if [ $? -eq 0 ]; then
        echo "✅ Constraints created successfully"
    else
        echo "❌ Failed to create constraints"
        exit 1
    fi
}

create_relationships() {
    echo "Creating relationships…"
    
    cypher-shell -u neo4j -p "$PASSWORD" <<'CYPHER'
CALL () {
  MATCH (r:results)
  MATCH (d:drivers)
  WHERE toInteger(r.driverId) = toInteger(d.driverId)
  MERGE (d)-[:ACHIEVED]->(r)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (r:results)
  MATCH (c:constructors)
  WHERE toInteger(r.constructorId) = toInteger(c.constructorId)
  MERGE (c)-[:ACHIEVED]->(r)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (ra:races)
  MATCH (ci:circuits)
  WHERE toInteger(ra.circuitId) = toInteger(ci.circuitId)
  MERGE (ra)-[:HELD_AT]->(ci)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (r:results)
  MATCH (ra:races)
  WHERE toInteger(r.raceId) = toInteger(ra.raceId)
  MERGE (r)-[:IN_RACE]->(ra)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (q:qualifying)
  MATCH (d:drivers)
  WHERE toInteger(q.driverId) = toInteger(d.driverId)
  MERGE (d)-[:QUALIFIED_IN]->(q)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (q:qualifying)
  MATCH (c:constructors)
  WHERE toInteger(q.constructorId) = toInteger(c.constructorId)
  MERGE (c)-[:QUALIFIED_IN]->(q)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (q:qualifying)
  MATCH (ra:races)
  WHERE toInteger(q.raceId) = toInteger(ra.raceId)
  MERGE (q)-[:FOR_RACE]->(ra)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (s:standings)
  MATCH (ra:races)
  WHERE toInteger(s.raceId) = toInteger(ra.raceId)
  MERGE (ra)-[:IN_STANDING]->(s)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (s:standings)
  MATCH (d:drivers)
  WHERE toInteger(s.driverId) = toInteger(d.driverId)
  MERGE (d)-[:ACHIEVED_STANDING]->(s)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (cs:constructor_results)
  MATCH (ra:races)
  WHERE toInteger(cs.raceId) = toInteger(ra.raceId)
  MERGE (ra)-[:RESULTED_IN]->(cs)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (cs:constructor_results)
  MATCH (c:constructors)
  WHERE toInteger(cs.constructorId) = toInteger(c.constructorId)
  MERGE (c)-[:RESULTED_IN]->(cs)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (cst:constructor_standings)
  MATCH (ra:races)
  WHERE toInteger(cst.raceId) = toInteger(ra.raceId)
  MERGE (ra)-[:HAS_STANDING]->(cst)
} IN TRANSACTIONS OF 1000 ROWS;

CALL () {
  MATCH (cst:constructor_standings)
  MATCH (c:constructors)
  WHERE toInteger(cst.constructorId) = toInteger(c.constructorId)
  MERGE (c)-[:HAS_STANDING]->(cst)
} IN TRANSACTIONS OF 1000 ROWS;
CYPHER

    if [ $? -eq 0 ]; then
        echo "✅ Relationships created successfully"
    else
        echo "❌ Failed to create relationships"
        exit 1
    fi
}

summary() {
    echo "Creating summary…"
    
    echo "Node counts:"
    cypher-shell -u neo4j -p "$PASSWORD" --non-interactive \
    "MATCH (n) RETURN labels(n)[0] AS NodeType, count(*) AS Count ORDER BY NodeType;"
    
    echo ""
    echo "Relationship counts:"
    cypher-shell -u neo4j -p "$PASSWORD" --non-interactive \
    "MATCH ()-[r]->() RETURN type(r) AS RelType, count(*) AS Count ORDER BY RelType;"
}

main() {
    echo "🚀 Starting Neo4j setup..."
    
    # Start Neo4j in background
    echo "📦 Starting Neo4j service..."
    /startup/docker-entrypoint.sh neo4j &
    
    # Wait for Neo4j to be ready
    wait_for_neo4j
    
    # Create constraints
    create_constraints
    
    # Create relationships  
    create_relationships
    
    # Show summary
    summary
    
    # Final setup
    echo "🔧 Setting up browser guides..."
    mkdir -p /var/lib/neo4j/import
    echo ":play http://localhost:7474/guides/verification-guide.html" > /var/lib/neo4j/import/startup.cypher
    echo "✅ Browser guides configured"

    echo ""
    echo "🎉 F1 Graph loaded successfully!"
    echo "🌐 Neo4j Browser: http://localhost:7474"
    echo "🔑 Username: neo4j"
    echo "🔑 Password: $PASSWORD"
    echo ""
    echo "🔍 To run verification queries, execute in browser:"
    echo "   :play http://localhost:7474/guides/verification-guide.html"
    echo ""
    echo "✨ Setup complete!"
}

main
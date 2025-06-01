#!/bin/bash

echo "=== Comprehensive F1 Graph Database Loader ==="
echo "Loading Formula 1 data into Neo4j..."

# Function to wait for Neo4j to be ready
wait_for_neo4j() {
    echo "Waiting for Neo4j to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if cypher-shell -u neo4j -p neo4jneo4j "RETURN 1" > /dev/null 2>&1; then
            echo "Neo4j is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - Neo4j not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "ERROR: Neo4j failed to start after $max_attempts attempts"
    exit 1
}

# Function to create constraints
create_constraints() {
    echo "Creating database constraints..."
    
    cypher-shell -u neo4j -p neo4jneo4j "
    CREATE CONSTRAINT circuit_id IF NOT EXISTS FOR (c:Circuit) REQUIRE c.circuitId IS UNIQUE;
    CREATE CONSTRAINT constructor_id IF NOT EXISTS FOR (c:Constructor) REQUIRE c.constructorId IS UNIQUE;
    CREATE CONSTRAINT driver_id IF NOT EXISTS FOR (d:Driver) REQUIRE d.driverId IS UNIQUE;
    CREATE CONSTRAINT race_id IF NOT EXISTS FOR (r:Race) REQUIRE r.raceId IS UNIQUE;
    CREATE CONSTRAINT result_id IF NOT EXISTS FOR (r:Result) REQUIRE r.resultId IS UNIQUE;
    CREATE CONSTRAINT qualifying_id IF NOT EXISTS FOR (q:Qualifying) REQUIRE q.qualifyId IS UNIQUE;
    " || {
        echo "WARNING: Some constraints may already exist"
    }
    
    echo "✓ Constraints created"
}

# Function to load nodes with proper ID extraction
load_nodes() {
    echo "=== Loading Nodes ==="
    
    echo "Loading Circuits..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///circuits_node.csv' AS row
    WITH row WHERE row.\`circuitId:ID(circuits):STRING\` IS NOT NULL
    CREATE (c:Circuit {
        circuitId: toInteger(split(row.\`circuitId:ID(circuits):STRING\`, '_')[1]),
        circuitRef: row.circuitRef,
        name: row.name,
        location: row.location,
        country: row.country,
        lat: toFloat(row.lat),
        lng: toFloat(row.lng),
        alt: CASE WHEN row.alt IS NOT NULL AND row.alt <> '' THEN toFloat(row.alt) ELSE null END
    });
    " && echo "✓ Circuits loaded" || echo "✗ Failed to load Circuits"
    
    echo "Loading Constructors..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///constructors_node.csv' AS row
    WITH row WHERE row.\`constructorId:ID(constructors):STRING\` IS NOT NULL
    CREATE (c:Constructor {
        constructorId: toInteger(split(row.\`constructorId:ID(constructors):STRING\`, '_')[1]),
        constructorRef: row.constructorRef,
        name: row.name,
        nationality: row.nationality
    });
    " && echo "✓ Constructors loaded" || echo "✗ Failed to load Constructors"
    
    echo "Loading Drivers..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///drivers_node.csv' AS row
    WITH row WHERE row.\`driverId:ID(drivers):STRING\` IS NOT NULL
    CREATE (d:Driver {
        driverId: toInteger(split(row.\`driverId:ID(drivers):STRING\`, '_')[1]),
        driverRef: row.driverRef,
        code: row.code,
        forename: row.forename,
        surname: row.surname,
        dob: date(row.dob),
        nationality: row.nationality
    });
    " && echo "✓ Drivers loaded" || echo "✗ Failed to load Drivers"
    
    echo "Loading Races..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///races_node.csv' AS row
    WITH row WHERE row.\`raceId:ID(races):STRING\` IS NOT NULL
    CREATE (r:Race {
        raceId: toInteger(split(row.\`raceId:ID(races):STRING\`, '_')[1]),
        year: toInteger(row.year),
        round: toInteger(row.round),
        circuitId: toInteger(row.circuitId),
        name: row.name,
        date: date(row.date),
        time: CASE WHEN row.time IS NOT NULL AND row.time <> '00:00:00' THEN time(row.time) ELSE null END
    });
    " && echo "✓ Races loaded" || echo "✗ Failed to load Races"
    
    echo "Loading Qualifying..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///qualifying_node.csv' AS row
    WITH row WHERE row.\`qualifyId:ID(qualifying):STRING\` IS NOT NULL
    CREATE (q:Qualifying {
        qualifyId: toInteger(split(row.\`qualifyId:ID(qualifying):STRING\`, '_')[1]),
        raceId: toInteger(row.raceId),
        driverId: toInteger(row.driverId),
        constructorId: toInteger(row.constructorId),
        number: toInteger(row.number),
        position: toInteger(row.position),
        date: date(row.date)
    });
    " && echo "✓ Qualifying loaded" || echo "✗ Failed to load Qualifying"
    
    echo "Loading Results..."
    cypher-shell -u neo4j -p neo4jneo4j "
    LOAD CSV WITH HEADERS FROM 'file:///results_node.csv' AS row
    WITH row WHERE row.\`resultId:ID(results):STRING\` IS NOT NULL
    CREATE (r:Result {
        resultId: toInteger(split(row.\`resultId:ID(results):STRING\`, '_')[1]),
        raceId: toInteger(row.raceId),
        driverId: toInteger(row.driverId),
        constructorId: toInteger(row.constructorId),
        number: CASE WHEN row.number IS NOT NULL AND row.number <> 'NULL' THEN toFloat(row.number) ELSE null END,
        grid: toInteger(row.grid),
        position: CASE WHEN row.position IS NOT NULL AND row.position <> 'NULL' THEN toFloat(row.position) ELSE null END,
        positionOrder: toInteger(row.positionOrder),
        points: toFloat(row.points),
        laps: toInteger(row.laps),
        milliseconds: CASE WHEN row.milliseconds IS NOT NULL AND row.milliseconds <> 'NULL' THEN toInteger(row.milliseconds) ELSE null END,
        fastestLap: CASE WHEN row.fastestLap IS NOT NULL AND row.fastestLap <> 'NULL' THEN toInteger(row.fastestLap) ELSE null END,
        rank: CASE WHEN row.rank IS NOT NULL AND row.rank <> 'NULL' THEN toInteger(row.rank) ELSE null END,
        statusId: toInteger(row.statusId),
        date: date(row.date)
    });
    " && echo "✓ Results loaded" || echo "✗ Failed to load Results"
}

# Function to create relationships
create_relationships() {
    echo "=== Creating Relationships ==="
    
    echo "Creating Result → Race relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (result:Result), (race:Race)
    WHERE result.raceId = race.raceId
    CREATE (result)-[:IN_RACE]->(race);
    " && echo "✓ IN_RACE relationships created"
    
    echo "Creating Driver → Result relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (result:Result), (driver:Driver)
    WHERE result.driverId = driver.driverId
    CREATE (driver)-[:ACHIEVED]->(result);
    " && echo "✓ Driver ACHIEVED relationships created"
    
    echo "Creating Constructor → Result relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (result:Result), (constructor:Constructor)
    WHERE result.constructorId = constructor.constructorId
    CREATE (constructor)-[:ACHIEVED]->(result);
    " && echo "✓ Constructor ACHIEVED relationships created"
    
    echo "Creating Race → Circuit relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (race:Race), (circuit:Circuit)
    WHERE race.circuitId = circuit.circuitId
    CREATE (race)-[:HELD_AT]->(circuit);
    " && echo "✓ HELD_AT relationships created"
    
    echo "Creating Driver → Qualifying relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (q:Qualifying), (d:Driver)
    WHERE q.driverId = d.driverId
    CREATE (d)-[:QUALIFIED_IN]->(q);
    " && echo "✓ Driver QUALIFIED_IN relationships created"
    
    echo "Creating Constructor → Qualifying relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (q:Qualifying), (c:Constructor)
    WHERE q.constructorId = c.constructorId
    CREATE (c)-[:QUALIFIED_IN]->(q);
    " && echo "✓ Constructor QUALIFIED_IN relationships created"
    
    echo "Creating Qualifying → Race relationships..."
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (q:Qualifying), (r:Race)
    WHERE q.raceId = r.raceId
    CREATE (q)-[:FOR_RACE]->(r);
    " && echo "✓ FOR_RACE relationships created"
}

# Function to generate summary
generate_summary() {
    echo "=== Database Summary ==="
    
    echo "Node counts:"
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (n) 
    RETURN labels(n)[0] as NodeType, count(n) as Count 
    ORDER BY NodeType;
    "
    
    echo ""
    echo "Relationship counts:"
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH ()-[r]->() 
    RETURN type(r) as RelType, count(r) as Count 
    ORDER BY RelType;
    "
    
    echo ""
    echo "Sample query - Hamilton's recent results:"
    cypher-shell -u neo4j -p neo4jneo4j "
    MATCH (d:Driver)-[:ACHIEVED]->(result:Result)-[:IN_RACE]->(race:Race)-[:HELD_AT]->(circuit:Circuit)
    WHERE d.surname = 'Hamilton'
    RETURN race.year, race.name, circuit.name, result.position, result.points
    ORDER BY race.year DESC, race.round DESC LIMIT 5;
    " || echo "No Hamilton results found (query failed)"
}

# Main execution
main() {
    echo "Starting F1 database import at $(date)"
    
    # Wait for Neo4j to be ready
    wait_for_neo4j
    
    # Clear any existing data
    echo "Clearing existing data..."
    cypher-shell -u neo4j -p neo4jneo4j "MATCH (n) DETACH DELETE n;" || echo "No existing data to clear"
    
    # Create constraints
    create_constraints
    
    # Load all nodes
    load_nodes
    
    # Create all relationships
    create_relationships
    
    # Generate summary
    generate_summary
    
    echo ""
    echo "🎉 F1 Graph Database Loading Complete!"
    echo "🌐 Access Neo4j Browser at: http://localhost:7474"
    echo "👤 Username: neo4j | Password: neo4jneo4j"
    echo ""
    echo "Ready for Cypher queries and text-to-Cypher conversion!"
}

# Execute main function
main
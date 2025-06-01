#!/bin/bash

# Start Neo4j in the background
echo "Starting Neo4j..."
/startup/docker-entrypoint.sh neo4j &

# Run the F1 database loader (using the correct path from Dockerfile)
/var/lib/neo4j/import-data.sh

# Keep the container running
echo "F1 database ready! Keeping container alive..."
wait

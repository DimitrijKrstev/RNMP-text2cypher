#!/bin/bash

# Collect all node and relationship CSV files dynamically
NODES=$(ls import/*_node.csv 2>/dev/null | paste -sd "," -)
RELATIONSHIPS=$(ls import/*_edge.csv 2>/dev/null | paste -sd "," -)

# Run the import command
neo4j-admin database import full formula1 --verbose --overwrite-destination \
    --nodes=$NODES --relationships=$RELATIONSHIPS


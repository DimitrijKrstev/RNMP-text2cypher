#!/bin/bash

DATASET_NAME=$1
if [ -z "$DATASET_NAME" ]; then
    echo "Usage: $0 <dataset_name>" 
    exit 1                         
fi

neo4j-admin database import full neo4j --verbose \
--overwrite-destination=true \
--id-type=string \
--report-file=import-report.txt \
--bad-tolerance=1000 \
--skip-bad-relationships=true \
--skip-duplicate-nodes=true \
--delimiter="," \
--array-delimiter=";" \
--multiline-fields=true \
$(for f in /var/lib/neo4j/import/*_nodes.csv; do [ -e "$f" ] && echo --nodes="$f"; done)

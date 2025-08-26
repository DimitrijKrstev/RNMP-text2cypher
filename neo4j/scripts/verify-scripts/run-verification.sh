#!/bin/sh
set -eu

# Inside container, we can use the environment variable directly
PASSWORD="neo4jneo4j"

echo "=== F1 Database Verification Report ==="
echo "Generated on: $(date)"
echo "========================================"

echo ""
echo "🔍 Running relationship verification..."
echo "----------------------------------------"
cypher-shell -u neo4j -p "$PASSWORD" -f /var/lib/neo4j/scripts/verify-scripts/verify-relationships.cypher --format verbose

echo ""
echo "🔍 Running data quality checks..."
echo "----------------------------------------"  
cypher-shell -u neo4j -p "$PASSWORD" -f /var/lib/neo4j/scripts/verify-scripts/verify-data-quality.cypher --format verbose

echo ""
echo "✅ Verification complete!"
echo "========================================"
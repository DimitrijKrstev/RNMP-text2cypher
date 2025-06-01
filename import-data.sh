#!/bin/bash

echo "=== Automated Graph Data Loader ==="
echo "Processing all CSV files in import directory..."

# Function to detect data types and generate appropriate Cypher conversion
detect_and_convert_field() {
    local field_name="$1"
    local sample_value="$2"
    
    # Check if it's an ID field
    if [[ "$field_name" == *"Id"* ]] || [[ "$field_name" == *"id"* ]]; then
        echo "toInteger(row.$field_name)"
    # Check if it's a numeric field (float)
    elif [[ "$sample_value" =~ ^-?[0-9]*\.[0-9]+$ ]]; then
        echo "toFloat(row.$field_name)"
    # Check if it's an integer
    elif [[ "$sample_value" =~ ^-?[0-9]+$ ]]; then
        echo "toInteger(row.$field_name)"
    # Check if it's a date (YYYY-MM-DD format)
    elif [[ "$sample_value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "date(row.$field_name)"
    # Check if it's a time (HH:MM:SS format)
    elif [[ "$sample_value" =~ ^[0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
        echo "time(row.$field_name)"
    # Default to string, but handle nulls
    else
        echo "CASE WHEN row.$field_name IS NOT NULL AND row.$field_name <> '' THEN row.$field_name ELSE null END"
    fi
}

# Function to generate node label from filename
get_node_label() {
    local filename="$1"
    # Extract base name and capitalize first letter
    local base_name=$(echo "$filename" | sed 's/_node\.csv$//' | sed 's/_/ /g' | sed 's/\b\w/\u&/g' | sed 's/ //g')
    echo "$base_name"
}

# Function to process node files
process_node_file() {
    local file="$1"
    local label=$(get_node_label "$file")
    
    echo "Processing node file: $file -> Label: $label"
    
    # Read first data row to detect types
    local first_data_row=$(sed -n '2p' "/var/lib/neo4j/import/$file")
    local headers=$(head -n 1 "/var/lib/neo4j/import/$file")
    
    # Convert headers to array
    IFS=',' read -ra header_array <<< "$headers"
    IFS=',' read -ra data_array <<< "$first_data_row"
    
    # Generate property mappings
    local properties=""
    for i in "${!header_array[@]}"; do
        local field="${header_array[i]}"
        local sample_value="${data_array[i]}"
        
        # Skip special Neo4j import columns
        if [[ "$field" == *":ID"* ]] || [[ "$field" == *":LABEL"* ]] || [[ "$field" == *":START_ID"* ]] || [[ "$field" == *":END_ID"* ]]; then
            continue
        fi
        
        # Clean field name (remove quotes)
        field=$(echo "$field" | tr -d '"')
        sample_value=$(echo "$sample_value" | tr -d '"')
        
        if [ ! -z "$field" ] && [ ! -z "$sample_value" ]; then
            local conversion=$(detect_and_convert_field "$field" "$sample_value")
            if [ ! -z "$properties" ]; then
                properties="$properties,\n    "
            fi
            properties="$properties$field: $conversion"
        fi
    done
    
    # Generate and execute Cypher query
    local cypher_query="
LOAD CSV WITH HEADERS FROM 'file:///$file' AS row
CREATE (n:$label {
    $properties
});"
    
    echo "Executing: Creating $label nodes..."
    cypher-shell -u neo4j -p password "$cypher_query"
}

# Function to process edge files
process_edge_file() {
    local file="$1"
    echo "Processing edge file: $file"
    
    # Try to determine relationship pattern from filename
    local rel_type=""
    local start_label=""
    local end_label=""
    
    # Parse common patterns
    if [[ "$file" == *"_"*"_edge.csv" ]]; then
        # Extract relationship info from filename
        local base_name=$(echo "$file" | sed 's/_edge\.csv$//')
        IFS='_' read -ra parts <<< "$base_name"
        
        if [ ${#parts[@]} -eq 2 ]; then
            start_label=$(echo "${parts[0]}" | sed 's/\b\w/\u&/g')
            end_label=$(echo "${parts[1]}" | sed 's/\b\w/\u&/g')
            rel_type="RELATED_TO"
        elif [ ${#parts[@]} -eq 3 ]; then
            start_label=$(echo "${parts[0]}" | sed 's/\b\w/\u&/g')
            rel_type=$(echo "${parts[1]}" | tr '[:lower:]' '[:upper:]')
            end_label=$(echo "${parts[2]}" | sed 's/\b\w/\u&/g')
        fi
    fi
    
    # Read headers to find ID columns
    local headers=$(head -n 1 "/var/lib/neo4j/import/$file")
    IFS=',' read -ra header_array <<< "$headers"
    
    local start_id_col=""
    local end_id_col=""
    
    for field in "${header_array[@]}"; do
        field=$(echo "$field" | tr -d '"')
        if [[ "$field" == *"Id"* ]] || [[ "$field" == *"id"* ]]; then
            if [ -z "$start_id_col" ]; then
                start_id_col="$field"
            else
                end_id_col="$field"
            fi
        fi
    done
    
    # Generate relationship query
    if [ ! -z "$start_id_col" ] && [ ! -z "$end_id_col" ] && [ ! -z "$start_label" ] && [ ! -z "$end_label" ]; then
        local cypher_query="
LOAD CSV WITH HEADERS FROM 'file:///$file' AS row
MATCH (a:$start_label), (b:$end_label)
WHERE a.${start_id_col} = toInteger(row.$start_id_col) 
  AND b.${end_id_col} = toInteger(row.$end_id_col)
CREATE (a)-[:$rel_type]->(b);"
        
        echo "Executing: Creating $start_label -[:$rel_type]-> $end_label relationships..."
        cypher-shell -u neo4j -p password "$cypher_query"
    else
        echo "Warning: Could not auto-detect relationship structure for $file"
        echo "Headers found: $headers"
    fi
}

# Main processing logic
echo "Creating constraints for common ID fields..."
cypher-shell -u neo4j -p password "
// Create constraints for common ID patterns
CREATE CONSTRAINT unique_circuit_id IF NOT EXISTS FOR (c:Circuit) REQUIRE c.circuitId IS UNIQUE;
CREATE CONSTRAINT unique_constructor_id IF NOT EXISTS FOR (c:Constructor) REQUIRE c.constructorId IS UNIQUE;
CREATE CONSTRAINT unique_driver_id IF NOT EXISTS FOR (d:Driver) REQUIRE d.driverId IS UNIQUE;
CREATE CONSTRAINT unique_race_id IF NOT EXISTS FOR (r:Race) REQUIRE r.raceId IS UNIQUE;
CREATE CONSTRAINT unique_result_id IF NOT EXISTS FOR (r:Result) REQUIRE r.resultId IS UNIQUE;
CREATE CONSTRAINT unique_qualify_id IF NOT EXISTS FOR (q:Qualifying) REQUIRE q.qualifyId IS UNIQUE;
"

echo ""
echo "=== PHASE 1: Processing Node Files ==="
# Process all node files first
for file in /var/lib/neo4j/import/*_node.csv; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        process_node_file "$filename"
        echo "✓ Completed: $filename"
        echo ""
    fi
done

echo ""
echo "=== PHASE 2: Processing Edge Files ==="
# Process all edge files
for file in /var/lib/neo4j/import/*_edge.csv; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        process_edge_file "$filename"
        echo "✓ Completed: $filename"
        echo ""
    fi
done

echo ""
echo "=== Import Summary ==="
cypher-shell -u neo4j -p password "
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) YIELD value
RETURN label as NodeType, value.count as Count
ORDER BY label;
"

echo ""
echo "Relationship Summary:"
cypher-shell -u neo4j -p password "
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run('MATCH ()-[r:' + relationshipType + ']->() RETURN count(r) as count', {}) YIELD value
RETURN relationshipType as RelationshipType, value.count as Count
ORDER BY relationshipType;
"

echo ""
echo "🎉 Automated graph loading completed!"
echo "Access Neo4j Browser at: http://localhost:7474"
echo "Username: neo4j, Password: password"

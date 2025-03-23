FROM neo4j:latest

# Copy import files
COPY import/ /var/lib/neo4j/import/

# Copy the import script
COPY import-data.sh /var/lib/neo4j/import-data.sh
RUN chmod +x /var/lib/neo4j/import-data.sh

WORKDIR /var/lib/neo4j

# Run the import script
RUN /var/lib/neo4j/import-data.sh

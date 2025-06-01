FROM neo4j:latest

# Copy import files
COPY import/ /var/lib/neo4j/import/

# Copy the comprehensive F1 import script
COPY f1-database-loader.sh /var/lib/neo4j/import-data.sh
RUN chmod +x /var/lib/neo4j/import-data.sh

WORKDIR /var/lib/neo4j

# Set environment variables
ENV NEO4J_AUTH=neo4j/neo4jneo4j

COPY docker-entrypoint-f1.sh /docker-entrypoint-f1.sh
RUN chmod +x /docker-entrypoint-f1.sh

ENTRYPOINT ["/docker-entrypoint-f1.sh"]
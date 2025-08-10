# check=skip=SecretsUsedInArgOrEnv
FROM neo4j:5.26.8 

ENV NEO4J_AUTH=neo4j/neo4jneo4j      \
  NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

COPY import/ /var/lib/neo4j/import/

COPY scripts/f1-database-loader.sh /var/lib/neo4j/f1-database-loader.sh
COPY scripts/import-nodes.sh /var/lib/neo4j/import-nodes.sh

RUN chmod +x /var/lib/neo4j/import-nodes.sh \
  && /var/lib/neo4j/import-nodes.sh
  
RUN chmod +x /var/lib/neo4j/f1-database-loader.sh \
  && /var/lib/neo4j/f1-database-loader.sh
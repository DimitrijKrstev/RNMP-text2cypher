# check=skip=SecretsUsedInArgOrEnv
FROM neo4j:5.26.8 

ARG DATASET_NAME=rel-f1
ENV NEO4J_AUTH=neo4j/neo4jneo4j \
    NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

COPY import/${DATASET_NAME}/ /var/lib/neo4j/import/
COPY scripts/ /var/lib/neo4j/scripts/
COPY scripts/constraints/ /var/lib/neo4j/scripts/

# Configure Neo4j to serve static content
RUN echo "dbms.directories.import=/var/lib/neo4j/import" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "browser.remote_content_hostname_whitelist=*" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "dbms.security.allow_csv_import_from_file_urls=true" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "server.memory.heap.initial_size=6G" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "server.memory.heap.max_size=6G" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "server.memory.pagecache.size=2G" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "db.memory.transaction.total.max=4G" >> /var/lib/neo4j/conf/neo4j.conf


RUN /var/lib/neo4j/scripts/import-nodes.sh ${DATASET_NAME}

ENV DATASET_NAME=${DATASET_NAME}
CMD ["/bin/bash", "-c", "/var/lib/neo4j/scripts/startup.sh $DATASET_NAME"]
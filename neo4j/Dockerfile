# check=skip=SecretsUsedInArgOrEnv
FROM neo4j:5.26.8 

ENV NEO4J_AUTH=neo4j/neo4jneo4j \
    NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

COPY import/ /var/lib/neo4j/import/
COPY scripts/ /var/lib/neo4j/scripts/
COPY scripts/create-constraints.cypher /var/lib/neo4j/scripts/

# Configure Neo4j to serve static content
RUN echo "dbms.directories.import=/var/lib/neo4j/import" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "browser.remote_content_hostname_whitelist=*" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "dbms.security.allow_csv_import_from_file_urls=true" >> /var/lib/neo4j/conf/neo4j.conf

RUN chmod +x /var/lib/neo4j/scripts/*.sh \
    && chmod +x /var/lib/neo4j/scripts/verify-scripts/*.sh

RUN /var/lib/neo4j/scripts/import-nodes.sh 

CMD ["/var/lib/neo4j/scripts/startup.sh"]
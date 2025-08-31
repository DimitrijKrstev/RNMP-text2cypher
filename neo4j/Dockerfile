# check=skip=SecretsUsedInArgOrEnv
FROM neo4j:5.26.8 

ENV NEO4J_AUTH=neo4j/neo4jneo4j \
    NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

# Copy all necessary files
COPY import/ /var/lib/neo4j/import/
COPY scripts/ /var/lib/neo4j/scripts/
COPY scripts/create-constraints.cypher /var/lib/neo4j/scripts/

# Configure Neo4j to serve static content
RUN echo "dbms.directories.import=/var/lib/neo4j/import" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "browser.remote_content_hostname_whitelist=*" >> /var/lib/neo4j/conf/neo4j.conf \
    && echo "dbms.security.allow_csv_import_from_file_urls=true" >> /var/lib/neo4j/conf/neo4j.conf

# Make scripts executable
RUN chmod +x /var/lib/neo4j/scripts/*.sh \
    && chmod +x /var/lib/neo4j/scripts/verify-scripts/*.sh

# Import nodes during build
RUN /var/lib/neo4j/scripts/import-nodes.sh

# Create startup script
RUN echo '#!/bin/sh' > /startup-script.sh \
    && echo 'set -eu' >> /startup-script.sh \
    && echo '' >> /startup-script.sh \
    && echo '# Setup in background' >> /startup-script.sh \
    && echo '(' >> /startup-script.sh \
    && echo '  echo "⏳ Waiting for Neo4j to start..."' >> /startup-script.sh \
    && echo '  while ! cypher-shell -u neo4j -p neo4jneo4j "RETURN 1" >/dev/null 2>&1; do' >> /startup-script.sh \
    && echo '    sleep 2' >> /startup-script.sh \
    && echo '  done' >> /startup-script.sh \
    && echo '  echo "✅ Neo4j is ready!"' >> /startup-script.sh \
    && echo '  echo "🔗 Creating relationships..."' >> /startup-script.sh \
    && echo '  /var/lib/neo4j/scripts/import-relationships.sh' >> /startup-script.sh \
    && echo '  echo "🔍 Running Database Verification..."' >> /startup-script.sh \
    && echo '  /var/lib/neo4j/scripts/verify-scripts/run-verification.sh' >> /startup-script.sh \
    && echo '  echo ""' >> /startup-script.sh \
    && echo '  echo "🎉 Setup complete! Neo4j is running at http://localhost:7474"' >> /startup-script.sh \
    && echo '  echo "🔑 Login: neo4j / neo4jneo4j"' >> /startup-script.sh \
    && echo ') &' >> /startup-script.sh \
    && echo '' >> /startup-script.sh \
    && echo 'exec /startup/docker-entrypoint.sh neo4j' >> /startup-script.sh \
    && chmod +x /startup-script.sh

CMD ["/var/lib/neo4j/scripts/startup.sh"]
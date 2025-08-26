// F1 Database Quick Queries
// =========================

// Overview
:play http://localhost:7474/guides/verification-guide.html

// Quick node count
MATCH (n) RETURN labels(n)[0] AS NodeType, count(*) AS Count ORDER BY NodeType;

// Quick relationship count  
MATCH ()-[r]->() RETURN type(r) AS RelType, count(*) AS Count ORDER BY RelType;

// Sample graph visualization
MATCH path = (d:drivers)-[:ACHIEVED]->(res:results)-[:IN_RACE]->(r:races)-[:HELD_AT]->(c:circuits)
WHERE d.code = 'HAM'
RETURN path LIMIT 5;

// Find popular circuits
MATCH (c:circuits)<-[:HELD_AT]-(r:races)
RETURN c.name AS circuit, count(*) AS races_held
ORDER BY races_held DESC LIMIT 10;
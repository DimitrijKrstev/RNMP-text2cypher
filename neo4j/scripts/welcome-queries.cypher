// Welcome to F1 Database!
// Copy these queries to explore your data

// 1. Overview of all node types
MATCH (n) 
RETURN labels(n)[0] AS NodeType, count(*) AS Count 
ORDER BY NodeType;

// 2. Overview of all relationships  
MATCH ()-[r]->() 
RETURN type(r) AS RelType, count(*) AS Count 
ORDER BY RelType;

// 3. Sample driver results
MATCH (d:drivers)-[:ACHIEVED]->(res:results)-[:IN_RACE]->(r:races)
RETURN d.code AS driver, res.position AS position, r.name AS race, r.year AS year
ORDER BY r.year DESC LIMIT 5;
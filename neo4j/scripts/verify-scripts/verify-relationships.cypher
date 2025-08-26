// RELATIONSHIP VERIFICATION QUERIES
// =================================

// 1. Node count summary
MATCH (n) 
RETURN labels(n)[0] AS NodeType, count(*) AS Count 
ORDER BY NodeType;

// 2. Relationship count summary
MATCH ()-[r]->() 
RETURN type(r) AS RelType, count(*) AS Count 
ORDER BY RelType;

// 3. Verify core F1 relationships exist
MATCH (d:drivers)-[r:ACHIEVED]->(res:results)
RETURN 'drivers->results' AS relationship, count(*) AS count;

MATCH (c:constructors)-[r:ACHIEVED]->(res:results)
RETURN 'constructors->results' AS relationship, count(*) AS count;

MATCH (r:races)-[rel:HELD_AT]->(c:circuits)
RETURN 'races->circuits' AS relationship, count(*) AS count;

MATCH (res:results)-[r:IN_RACE]->(ra:races)
RETURN 'results->races' AS relationship, count(*) AS count;

// 5. Find orphaned nodes
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n)[0] AS OrphanType, count(*) AS OrphanCount
ORDER BY OrphanType;

// 6. Verify qualifying relationships
MATCH (d:drivers)-[r:QUALIFIED_IN]->(q:qualifying)
RETURN 'drivers->qualifying' AS relationship, count(*) AS count;

MATCH (c:constructors)-[r:QUALIFIED_IN]->(q:qualifying)
RETURN 'constructors->qualifying' AS relationship, count(*) AS count;

MATCH (q:qualifying)-[r:FOR_RACE]->(ra:races)
RETURN 'qualifying->races' AS relationship, count(*) AS count;

// 7. Verify standings relationships
MATCH (ra:races)-[r:IN_STANDING]->(s:standings)
RETURN 'races->standings' AS relationship, count(*) AS count;

MATCH (d:drivers)-[r:ACHIEVED_STANDING]->(s:standings)
RETURN 'drivers->standings' AS relationship, count(*) AS count;

// 8. Constructor-specific relationships
MATCH (ra:races)-[r:RESULTED_IN]->(cs:constructor_results)
RETURN 'races->constructor_results' AS relationship, count(*) AS count;

MATCH (c:constructors)-[r:RESULTED_IN]->(cs:constructor_results)
RETURN 'constructors->constructor_results' AS relationship, count(*) AS count;

MATCH (ra:races)-[r:HAS_STANDING]->(cst:constructor_standings)
RETURN 'races->constructor_standings' AS relationship, count(*) AS count;

MATCH (c:constructors)-[r:HAS_STANDING]->(cst:constructor_standings)
RETURN 'constructors->constructor_standings' AS relationship, count(*) AS count;

// 9. Sample complete paths to verify data flow
MATCH path = (d:drivers)-[:ACHIEVED]->(res:results)-[:IN_RACE]->(r:races)
RETURN d.code AS driver, res.position AS position, 
       r.name AS race, r.year AS year
LIMIT 5;

// 10. Relationship density analysis
MATCH (d:drivers) WITH count(*) AS drivers
MATCH (res:results) WITH drivers, count(*) AS results  
MATCH (r:races) WITH drivers, results, count(*) AS races
RETURN drivers, races, results,
       round(results * 1.0 / drivers) AS avg_results_per_driver,
       round(results * 1.0 / races) AS avg_results_per_race;
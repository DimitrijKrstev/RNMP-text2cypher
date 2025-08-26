// DATA QUALITY VERIFICATION QUERIES
// =================================

// 1. Check for NULL or empty critical fields
MATCH (d:drivers)
WHERE d.driverId IS NULL OR d.code IS NULL OR d.surname IS NULL
RETURN 'drivers' AS table_name, count(*) AS null_critical_fields;

MATCH (c:circuits)
WHERE c.circuitId IS NULL OR c.name IS NULL
RETURN 'circuits' AS table_name, count(*) AS null_critical_fields;

MATCH (r:races)
WHERE r.raceId IS NULL OR r.year IS NULL
RETURN 'races' AS table_name, count(*) AS null_critical_fields;

// 2. Check for duplicate IDs within each node type
MATCH (d:drivers)
WITH d.driverId AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'drivers' AS table_name, id, cnt AS duplicate_count;

MATCH (c:circuits)
WITH c.circuitId AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'circuits' AS table_name, id, cnt AS duplicate_count;

MATCH (r:races)
WITH r.raceId AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'races' AS table_name, id, cnt AS duplicate_count;

// 3. Check for referential integrity issues
// Results without matching drivers
MATCH (res:results)
WHERE NOT EXISTS {
    MATCH (d:drivers)
    WHERE toInteger(res.driverId) = toInteger(d.driverId)
}
RETURN 'results_without_drivers' AS issue, count(*) AS count;

// Results without matching constructors
MATCH (res:results)
WHERE NOT EXISTS {
    MATCH (c:constructors)
    WHERE toInteger(res.constructorId) = toInteger(c.constructorId)
}
RETURN 'results_without_constructors' AS issue, count(*) AS count;

// Results without matching races
MATCH (res:results)
WHERE NOT EXISTS {
    MATCH (r:races)
    WHERE toInteger(res.raceId) = toInteger(r.raceId)
}
RETURN 'results_without_races' AS issue, count(*) AS count;

// Races without matching circuits (will show the typo impact)
MATCH (r:races)
WHERE NOT EXISTS {
    MATCH (c:circuits)
    WHERE toInteger(r.circuitId) = toInteger(c.circuitId)
}
RETURN 'races_without_circuits' AS issue, count(*) AS count;

// 4. Check for data range anomalies
// Impossible positions (should be 1-20 typically)
MATCH (res:results)
WHERE toInteger(res.position) < 1 OR toInteger(res.position) > 30
RETURN 'invalid_positions' AS issue, count(*) AS count, 
       min(toInteger(res.position)) AS min_pos, 
       max(toInteger(res.position)) AS max_pos;

// Negative or excessive points
MATCH (res:results)
WHERE toFloat(res.points) < 0 OR toFloat(res.points) > 50
RETURN 'unusual_points' AS issue, count(*) AS count,
       min(toFloat(res.points)) AS min_points,
       max(toFloat(res.points)) AS max_points;

// 5. Check temporal consistency
// Races in impossible years
MATCH (r:races)
WHERE toInteger(r.year) < 1950 OR toInteger(r.year) > 2024
RETURN 'races_unusual_years' AS issue, count(*) AS count,
       min(toInteger(r.year)) AS min_year,
       max(toInteger(r.year)) AS max_year;

// 6. Check for missing relationships that should exist
// Drivers who have results but no qualifying data
MATCH (d:drivers)-[:ACHIEVED]->(res:results)
WHERE NOT EXISTS {
    MATCH (d)-[:QUALIFIED_IN]->(:qualifying)
}
WITH d, count(res) AS result_count
RETURN 'drivers_results_no_qualifying' AS issue, count(*) AS driver_count,
       sum(result_count) AS total_results_affected;

// 7. Check relationship direction consistency
// Make sure all relationships go in the expected direction
MATCH (res:results)-[:ACHIEVED]->(d:drivers)
RETURN 'wrong_direction_driver_achieved' AS issue, count(*) AS count;

MATCH (c:circuits)-[:HELD_AT]->(r:races)
RETURN 'wrong_direction_held_at' AS issue, count(*) AS count;

// 8. Statistical anomalies
// Drivers with unusually high number of results
MATCH (d:drivers)-[:ACHIEVED]->(res:results)
WITH d, count(res) AS result_count
WHERE result_count > 500  // Adjust threshold based on data
RETURN 'drivers_excessive_results' AS issue, 
       d.code AS driver_code, 
       result_count;

// Constructors with unusually high number of results
MATCH (c:constructors)-[:ACHIEVED]->(res:results)
WITH c, count(res) AS result_count
WHERE result_count > 1000  // Adjust threshold based on data
RETURN 'constructors_excessive_results' AS issue,
       c.name AS constructor_name,
       result_count;

// 9. Check for orphaned relationship nodes
// Results not connected to races
MATCH (res:results)
WHERE NOT (res)-[:IN_RACE]->(:races)
RETURN 'orphaned_results' AS issue, count(*) AS count;

// Qualifying not connected to races
MATCH (q:qualifying)
WHERE NOT (q)-[:FOR_RACE]->(:races)
RETURN 'orphaned_qualifying' AS issue, count(*) AS count;

// 10. Data completeness check
// Count missing optional but important fields
MATCH (res:results)
WHERE res.fastestLapTime IS NULL
RETURN 'results_missing_fastest_lap' AS metric, count(*) AS count;

MATCH (res:results)
WHERE res.statusId IS NULL
RETURN 'results_missing_status' AS metric, count(*) AS count;

// 11. Cross-reference consistency
// Check if qualifying and results have same drivers for same race
MATCH (r:races)<-[:FOR_RACE]-(q:qualifying)
MATCH (r)<-[:IN_RACE]-(res:results)
WHERE toInteger(q.driverId) = toInteger(res.driverId)
WITH r, count(DISTINCT q.driverId) AS qualifying_drivers, 
     count(DISTINCT res.driverId) AS result_drivers
WHERE qualifying_drivers <> result_drivers
RETURN 'race_driver_mismatch' AS issue, count(*) AS races_affected;

// 12. Summary statistics for validation
MATCH (n)
RETURN labels(n)[0] AS node_type, count(*) AS total_count
ORDER BY node_type;

MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(*) AS total_count
ORDER BY relationship_type;
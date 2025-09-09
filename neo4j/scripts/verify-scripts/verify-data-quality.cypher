//  all counts should be zero


// 1. range checks
// positions outside realistic range
MATCH (res:results)
WHERE res.position IS NOT NULL
  AND (toInteger(res.position) < 1 OR toInteger(res.position) > 30)
RETURN 'invalid_position' AS issue, count(*) AS cnt;

// negative or excessive points
MATCH (res:results)
WHERE toFloat(res.points) < 0 OR toFloat(res.points) > 50
RETURN 'unusual_points' AS issue, count(*) AS cnt;

// implausible race years
MATCH (ra:races)
WHERE toInteger(ra.year) < 1950 OR toInteger(ra.year) > 2024
RETURN 'implausible_year' AS issue,
       count(*)                 AS cnt,
       min(toInteger(ra.year))  AS minYear,
       max(toInteger(ra.year))  AS maxYear;

// 2. duplicate PKs

MATCH (n:drivers)
WITH n.driverId AS id, count(*) AS c WHERE c>1
RETURN 'dup_driverId' AS issue, sum(c) AS cnt;

MATCH (n:constructors)
WITH n.constructorId AS id, count(*) AS c WHERE c>1
RETURN 'dup_constructorId' AS issue, sum(c) AS cnt;

MATCH (n:circuits)
WITH n.circuitId AS id, count(*) AS c WHERE c>1
RETURN 'dup_circuitId' AS issue, sum(c) AS cnt;

MATCH (n:races)
WITH n.raceId AS id, count(*) AS c WHERE c>1
RETURN 'dup_raceId' AS issue, sum(c) AS cnt;

MATCH (n:results)
WITH n.resultId AS id, count(*) AS c WHERE c>1
RETURN 'dup_resultId' AS issue, sum(c) AS cnt;

MATCH (n:qualifying)
WITH n.qualifyId AS id, count(*) AS c WHERE c>1
RETURN 'dup_qualifyId' AS issue, sum(c) AS cnt;

// 3. completeness

MATCH (res:results)
WHERE res.fastestLapTime IS NULL
RETURN 'results_missing_fastLap' AS issue, count(*) AS cnt;

MATCH (res:results)
WHERE res.statusId IS NULL
RETURN 'results_missing_status' AS issue, count(*) AS cnt;

// 4. qualifyingvs results driver match

MATCH (ra:races)<-[:FOR_RACE]-(q:qualifying)
MATCH (ra)<-[:IN_RACE]-(res:results)
WITH ra,
     collect(DISTINCT q.driverId)   AS qDrivers,
     collect(DISTINCT res.driverId) AS rDrivers
WHERE size([d IN qDrivers WHERE NOT d IN rDrivers]) > 0
   OR size([d IN rDrivers WHERE NOT d IN qDrivers]) > 0
RETURN 'race_driver_mismatch' AS issue, count(*) AS racesAffected;

// 5. Position/Driver Points missmatch
MATCH (d:drivers)-[:ACHIEVED]->(r:results)
WHERE r.position <= 3 AND toFloat(r.points) = 0
RETURN count(r);

// 6. Fastest lap must be exactly one
MATCH (ra:races)<-[:IN_RACE]-(r:results)
WITH ra,
     sum( CASE WHEN r.fastestLapTime IS NOT NULL THEN 1 ELSE 0 END ) AS laps
WHERE laps > 1
RETURN ra.raceId AS raceId, laps;

// 7. a season without 20 races
MATCH (ra:races) 
WITH ra.year AS yr, count(*) AS races  
WHERE races <> 20
RETURN yr, races;

// 1.  Summary
MATCH (n) RETURN labels(n)[0] AS node, count(*) AS cnt ORDER BY node;
MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS cnt ORDER BY rel;

// 2.  Orphaned nodes
MATCH (n) WHERE NOT (n)--()
RETURN labels(n)[0] AS orphanType, count(*) AS cnt;

// 3.  Referential-integrity violations  (each should be 0)
RETURN
  count { MATCH (r:results)
          WHERE NOT EXISTS { MATCH (d:drivers {driverId:r.driverId}) } }      AS results_without_driver,

  count { MATCH (r:results)
          WHERE NOT EXISTS { MATCH (ra:races {raceId:r.raceId}) } }           AS results_without_race,

  count { MATCH (ra:races)
          WHERE NOT EXISTS { MATCH (c:circuits
                                     {circuitId:coalesce(ra.circuitId,ra.circutId)}) } }
                                                                              AS races_without_circuit,

  count { MATCH (q:qualifying)
          WHERE NOT EXISTS { MATCH (d:drivers {driverId:q.driverId}) } }      AS qual_without_driver;

// 4.  Relationship density
MATCH (d:drivers)-->(res:results)
WITH count(res) AS totalRes, count(DISTINCT d) AS totalDrv
RETURN totalDrv,
       totalRes,
       round(1.0*totalRes/totalDrv,1) AS avgResPerDriver;
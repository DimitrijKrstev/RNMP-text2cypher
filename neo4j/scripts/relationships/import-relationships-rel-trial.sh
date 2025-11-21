#!/usr/bin/env bash
set -euo pipefail
BATCH=25
USER=neo4j
PASS=${NEO4J_PASSWORD:-${NEO4J_AUTH#neo4j/}}

run() {
  cypher-shell -u "$USER" -p "$PASS" --non-interactive "$1"
}

echo "------ Building relationships in batches of $BATCH ------"

run "CALL { MATCH (o:outcomes) MATCH (s:studies {nct_id: o.nct_id}) MERGE (s)-[:HAS_OUTCOME]->(o) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (oa:outcome_analyses) MATCH (o:outcomes {nct_id: oa.nct_id, id: oa.outcome_id}) MERGE (o)-[:HAS_ANALYSIS]->(oa) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (d:designs) MATCH (s:studies {nct_id: d.nct_id}) MERGE (s)-[:HAS_DESIGN]->(d) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (dw:drop_withdrawals) MATCH (s:studies {nct_id: dw.nct_id}) MERGE (s)-[:HAS_WITHDRAWAL]->(dw) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (e:eligibilities) MATCH (s:studies {nct_id: e.nct_id}) MERGE (s)-[:HAS_ELIGIBILITY]->(e) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (ret:reported_event_totals) MATCH (s:studies {nct_id: ret.nct_id}) MERGE (s)-[:HAS_EVENT_TOTAL]->(ret) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (is:interventions_studies) MATCH (s:studies {nct_id: is.nct_id}) MERGE (s)-[:HAS_INTERVENTION_RECORD]->(is) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (is:interventions_studies) MATCH (i:interventions {intervention_id: is.intervention_id}) MERGE (is)-[:FOR_INTERVENTION]->(i) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (fs:facilities_studies) MATCH (s:studies {nct_id: fs.nct_id}) MERGE (s)-[:HAS_FACILITY_RECORD]->(fs) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (fs:facilities_studies) MATCH (f:facilities {facility_id: fs.facility_id}) MERGE (fs)-[:AT_FACILITY]->(f) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (ss:sponsors_studies) MATCH (s:studies {nct_id: ss.nct_id}) MERGE (s)-[:HAS_SPONSOR_RECORD]->(ss) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (ss:sponsors_studies) MATCH (sp:sponsors {sponsor_id: ss.sponsor_id}) MERGE (ss)-[:BY_SPONSOR]->(sp) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (cs:conditions_studies) MATCH (s:studies {nct_id: cs.nct_id}) MERGE (s)-[:HAS_CONDITION_RECORD]->(cs) } IN TRANSACTIONS OF $BATCH ROWS;"

run "CALL { MATCH (cs:conditions_studies) MATCH (c:conditions {condition_id: cs.condition_id}) MERGE (cs)-[:FOR_CONDITION]->(c) } IN TRANSACTIONS OF $BATCH ROWS;"

echo "------ Relationship import finished ------"
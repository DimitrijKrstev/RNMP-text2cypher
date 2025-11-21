// Primary Key Constraints
CREATE CONSTRAINT studies_pk IF NOT EXISTS FOR (n:studies) REQUIRE n.nct_id IS UNIQUE;
CREATE CONSTRAINT outcomes_pk IF NOT EXISTS FOR (n:outcomes) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT outcome_analyses_pk IF NOT EXISTS FOR (n:outcome_analyses) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT drop_withdrawals_pk IF NOT EXISTS FOR (n:drop_withdrawals) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT designs_pk IF NOT EXISTS FOR (n:designs) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT eligibilities_pk IF NOT EXISTS FOR (n:eligibilities) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT reported_event_totals_pk IF NOT EXISTS FOR (n:reported_event_totals) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT interventions_pk IF NOT EXISTS FOR (n:interventions) REQUIRE n.intervention_id IS UNIQUE;
CREATE CONSTRAINT interventions_studies_pk IF NOT EXISTS FOR (n:interventions_studies) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT facilities_pk IF NOT EXISTS FOR (n:facilities) REQUIRE n.facility_id IS UNIQUE;
CREATE CONSTRAINT facilities_studies_pk IF NOT EXISTS FOR (n:facilities_studies) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT sponsors_pk IF NOT EXISTS FOR (n:sponsors) REQUIRE n.sponsor_id IS UNIQUE;
CREATE CONSTRAINT sponsors_studies_pk IF NOT EXISTS FOR (n:sponsors_studies) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT conditions_pk IF NOT EXISTS FOR (n:conditions) REQUIRE n.condition_id IS UNIQUE;
CREATE CONSTRAINT conditions_studies_pk IF NOT EXISTS FOR (n:conditions_studies) REQUIRE n.id IS UNIQUE;

// Foreign Key Indexes
CREATE INDEX outcomes_study_fk IF NOT EXISTS FOR (n:outcomes) ON (n.nct_id);
CREATE INDEX outcome_analyses_study_fk IF NOT EXISTS FOR (n:outcome_analyses) ON (n.nct_id);
CREATE INDEX outcome_analyses_outcome_fk IF NOT EXISTS FOR (n:outcome_analyses) ON (n.outcome_id);
CREATE INDEX drop_withdrawals_study_fk IF NOT EXISTS FOR (n:drop_withdrawals) ON (n.nct_id);
CREATE INDEX designs_study_fk IF NOT EXISTS FOR (n:designs) ON (n.nct_id);
CREATE INDEX eligibilities_study_fk IF NOT EXISTS FOR (n:eligibilities) ON (n.nct_id);
CREATE INDEX reported_event_totals_study_fk IF NOT EXISTS FOR (n:reported_event_totals) ON (n.nct_id);
CREATE INDEX interventions_studies_study_fk IF NOT EXISTS FOR (n:interventions_studies) ON (n.nct_id);
CREATE INDEX interventions_studies_intervention_fk IF NOT EXISTS FOR (n:interventions_studies) ON (n.intervention_id);
CREATE INDEX facilities_studies_study_fk IF NOT EXISTS FOR (n:facilities_studies) ON (n.nct_id);
CREATE INDEX facilities_studies_facility_fk IF NOT EXISTS FOR (n:facilities_studies) ON (n.facility_id);
CREATE INDEX sponsors_studies_study_fk IF NOT EXISTS FOR (n:sponsors_studies) ON (n.nct_id);
CREATE INDEX sponsors_studies_sponsor_fk IF NOT EXISTS FOR (n:sponsors_studies) ON (n.sponsor_id);
CREATE INDEX conditions_studies_study_fk IF NOT EXISTS FOR (n:conditions_studies) ON (n.nct_id);
CREATE INDEX conditions_studies_condition_fk IF NOT EXISTS FOR (n:conditions_studies) ON (n.condition_id);
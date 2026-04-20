CREATE OR REPLACE TABLE conditions (
    condition_id BIGINT PRIMARY KEY,
    mesh_term VARCHAR
);

CREATE OR REPLACE TABLE interventions (
    intervention_id BIGINT PRIMARY KEY,
    mesh_term VARCHAR
);

CREATE OR REPLACE TABLE sponsors (
    sponsor_id BIGINT PRIMARY KEY,
    name VARCHAR,
    agency_class VARCHAR
);

CREATE OR REPLACE TABLE studies (
    nct_id BIGINT,
    start_date TIMESTAMP,
    target_duration VARCHAR,
    study_type VARCHAR,
    acronym VARCHAR,
    baseline_population VARCHAR,
    brief_title VARCHAR,
    official_title VARCHAR,
    phase VARCHAR,
    enrollment DOUBLE,
    enrollment_type VARCHAR,
    source VARCHAR,
    limitations_and_caveats DOUBLE,
    number_of_arms DOUBLE,
    number_of_groups DOUBLE,
    has_dmc VARCHAR,
    is_fda_regulated_drug VARCHAR,
    is_fda_regulated_device VARCHAR,
    is_unapproved_device VARCHAR,
    is_ppsd VARCHAR,
    is_us_export VARCHAR,
    biospec_retention VARCHAR,
    biospec_description VARCHAR,
    source_class VARCHAR,
    baseline_type_units_analyzed VARCHAR,
    fdaaa801_violation VARCHAR,
    plan_to_share_ipd VARCHAR,
    detailed_descriptions VARCHAR,
    brief_summaries VARCHAR
);

CREATE OR REPLACE TABLE facilities (
    facility_id BIGINT,
    name VARCHAR,
    city VARCHAR,
    state VARCHAR,
    zip VARCHAR,
    country VARCHAR
);

CREATE OR REPLACE TABLE outcomes (
    id BIGINT,
    nct_id BIGINT,
    outcome_type VARCHAR,
    title VARCHAR,
    description VARCHAR,
    time_frame VARCHAR,
    population VARCHAR,
    units VARCHAR,
    units_analyzed VARCHAR,
    dispersion_type VARCHAR,
    param_type VARCHAR,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE designs (
    id BIGINT,
    nct_id BIGINT,
    allocation VARCHAR,
    intervention_model VARCHAR,
    observational_model VARCHAR,
    primary_purpose VARCHAR,
    time_perspective VARCHAR,
    masking VARCHAR,
    masking_description VARCHAR,
    intervention_model_description VARCHAR,
    subject_masked VARCHAR,
    caregiver_masked VARCHAR,
    investigator_masked VARCHAR,
    outcomes_assessor_masked VARCHAR,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE eligibilities (
    id BIGINT,
    nct_id BIGINT,
    sampling_method VARCHAR,
    gender VARCHAR,
    minimum_age VARCHAR,
    maximum_age VARCHAR,
    healthy_volunteers VARCHAR,
    population VARCHAR,
    criteria VARCHAR,
    gender_description VARCHAR,
    gender_based VARCHAR,
    adult VARCHAR,
    child VARCHAR,
    older_adult VARCHAR,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE drop_withdrawals (
    id BIGINT,
    nct_id BIGINT,
    period VARCHAR,
    reason VARCHAR,
    count DOUBLE,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE reported_event_totals (
    id BIGINT,
    nct_id BIGINT,
    event_type VARCHAR,
    classification VARCHAR,
    subjects_affected DOUBLE,
    subjects_at_risk DOUBLE,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE conditions_studies (
    id BIGINT,
    nct_id BIGINT,
    condition_id BIGINT,
    date TIMESTAMP,
    FOREIGN KEY (condition_id) REFERENCES conditions(condition_id)
);

CREATE OR REPLACE TABLE interventions_studies (
    id BIGINT,
    nct_id BIGINT,
    intervention_id BIGINT,
    date TIMESTAMP,
    FOREIGN KEY (intervention_id) REFERENCES interventions(intervention_id)
);

CREATE OR REPLACE TABLE sponsors_studies (
    id BIGINT,
    nct_id BIGINT,
    sponsor_id BIGINT,
    lead_or_collaborator VARCHAR,
    date TIMESTAMP,
    FOREIGN KEY (sponsor_id) REFERENCES sponsors(sponsor_id)
);

CREATE OR REPLACE TABLE facilities_studies (
    id BIGINT,
    nct_id BIGINT,
    facility_id BIGINT,
    date TIMESTAMP
);

CREATE OR REPLACE TABLE outcome_analyses (
    id BIGINT,
    nct_id BIGINT,
    outcome_id BIGINT,
    non_inferiority_type VARCHAR,
    non_inferiority_description VARCHAR,
    param_type VARCHAR,
    param_value DOUBLE,
    dispersion_type VARCHAR,
    dispersion_value DOUBLE,
    p_value_modifier VARCHAR,
    p_value DOUBLE,
    ci_n_sides VARCHAR,
    ci_percent DOUBLE,
    ci_lower_limit DOUBLE,
    ci_upper_limit DOUBLE,
    ci_upper_limit_na_comment VARCHAR,
    p_value_description VARCHAR,
    method VARCHAR,
    method_description VARCHAR,
    estimate_description VARCHAR,
    groups_description VARCHAR,
    other_analysis_description VARCHAR,
    ci_upper_limit_raw DOUBLE,
    ci_lower_limit_raw DOUBLE,
    p_value_raw DOUBLE,
    date TIMESTAMP
);

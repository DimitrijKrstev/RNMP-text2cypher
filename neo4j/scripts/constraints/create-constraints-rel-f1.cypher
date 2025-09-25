// Idempotent PK constraints
CREATE CONSTRAINT circuits_pk              IF NOT EXISTS FOR (n:circuits)              REQUIRE n.circuitId              IS UNIQUE;
CREATE CONSTRAINT constructors_pk          IF NOT EXISTS FOR (n:constructors)          REQUIRE n.constructorId          IS UNIQUE;
CREATE CONSTRAINT drivers_pk               IF NOT EXISTS FOR (n:drivers)               REQUIRE n.driverId               IS UNIQUE;
CREATE CONSTRAINT races_pk                 IF NOT EXISTS FOR (n:races)                 REQUIRE n.raceId                 IS UNIQUE;
CREATE CONSTRAINT results_pk               IF NOT EXISTS FOR (n:results)               REQUIRE n.resultId               IS UNIQUE;
CREATE CONSTRAINT qualifying_pk            IF NOT EXISTS FOR (n:qualifying)            REQUIRE n.qualifyId              IS UNIQUE;
CREATE CONSTRAINT standings_pk             IF NOT EXISTS FOR (n:standings)             REQUIRE n.standingId             IS UNIQUE;
CREATE CONSTRAINT constructor_results_pk   IF NOT EXISTS FOR (n:constructor_results)   REQUIRE n.constructorResultId    IS UNIQUE;
CREATE CONSTRAINT constructor_standings_pk IF NOT EXISTS FOR (n:constructor_standings) REQUIRE n.constructorStandingId  IS UNIQUE;

// Helpful FK indexes
CREATE INDEX results_driver_fk      IF NOT EXISTS FOR (n:results)               ON (n.driverId);
CREATE INDEX results_constructor_fk IF NOT EXISTS FOR (n:results)               ON (n.constructorId);
CREATE INDEX results_race_fk        IF NOT EXISTS FOR (n:results)               ON (n.raceId);
CREATE INDEX races_circuit_fk       IF NOT EXISTS FOR (n:races)                 ON (n.circuitId);
CREATE INDEX qualifying_driver_fk   IF NOT EXISTS FOR (n:qualifying)            ON (n.driverId);
CREATE INDEX qualifying_constructor_fk IF NOT EXISTS FOR (n:qualifying)         ON (n.constructorId);
CREATE INDEX qualifying_race_fk     IF NOT EXISTS FOR (n:qualifying)            ON (n.raceId);
CREATE INDEX standings_driver_fk    IF NOT EXISTS FOR (n:standings)             ON (n.driverId);
CREATE INDEX standings_race_fk      IF NOT EXISTS FOR (n:standings)             ON (n.raceId);
CREATE INDEX constructor_results_fk IF NOT EXISTS FOR (n:constructor_results)   ON (n.constructorId, n.raceId);
CREATE INDEX constructor_standings_fk IF NOT EXISTS FOR (n:constructor_standings) ON (n.constructorId, n.raceId);
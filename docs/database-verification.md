# Database Verification Guide

## Relationship Schema

### Node Types
- `circuits`: F1 racing circuits
- `drivers`: F1 drivers
- `constructors`: F1 teams/constructors
- `races`: Individual race events
- `results`: Race results
- `qualifying`: Qualifying session results
- `standings`: Driver championship standings
- `constructor_results`: Constructor race results
- `constructor_standings`: Constructor championship standings

### Relationships
- `drivers -[ACHIEVED]-> results`
- `constructors -[ACHIEVED]-> results`
- `races -[HELD_AT]-> circuits`
- `results -[IN_RACE]-> races`
- `drivers -[QUALIFIED_IN]-> qualifying`
- `constructors -[QUALIFIED_IN]-> qualifying`
- `qualifying -[FOR_RACE]-> races`
- `races -[IN_STANDING]-> standings`
- `drivers -[ACHIEVED_STANDING]-> standings`
- `races -[RESULTED_IN]-> constructor_results`
- `constructors -[RESULTED_IN]-> constructor_results`
- `races -[HAS_STANDING]-> constructor_standings`
- `constructors -[HAS_STANDING]-> constructor_standings`

## Expected Counts
[Document expected ranges after running verification]

## Known Issues
- Typo in circuit relationship: `circutId` vs `circuitId`
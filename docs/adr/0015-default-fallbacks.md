# Architectural Decision Record 0015 - Graceful Degradation and Default Fallbacks

## Module: data_initialization.py
## Tags: #DATA-INT, #PAYLOAD-CONSTRUCTION, #FAULT-TOLERANCE
## Status: Accepted

### Context
During payload construction, users may request an Artist, Genre, or Track Scale that does not exist or has been deleted from the live SQL schema. If the initialization logic strictly demands an exact match, the entire generation pipeline will crash, halting mass generation scripts over minor metadata mismatches.

### Decision
Implement dynamic, database-driven fallbacks across the initialization module.

* Functions like `fetch_artist`, `fetch_genre`, and `fetch_track_scale` execute a query for the requested name. If it evaluates to None, the system triggers a warning and automatically issues a *random.choice()* against all valid remaining entries in the database.

### Consequences
* **Requirement**: The database must have at least one valid entry for every core metadata type (Artist, Genre, Track, Scale) to survive a fallback request.

* **Stability**: The orchestrator is immune to null-reference crashes caused by invalid user string inputs or missing SQL junction mappings.
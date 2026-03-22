# Architectural Decision Record 0011 - Metadata Upload Genre Caching
## Tags: #PERF-OPT, #DATA-FLOW
## Status: Accepted

### Context
During batch metadata ingestion, querying the database for a parent `Genre` on every single row of a large CSV caused severe I/O bottlenecking, drastically slowing down mass imports.

### Decision
Implement a local `get_genre()` dictionary cache within the ingestor class. The database is queried once per unique genre name; subsequent requests retrieve the ORM object directly from the in-memory cache.

### Consequences
* **Performance**: Reduces read queries by orders of magnitude during heavy CSV batch processing.
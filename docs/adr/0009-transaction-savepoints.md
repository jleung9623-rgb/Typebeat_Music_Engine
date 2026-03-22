# Architectural Decision Record 0009 - Transaction Savepoints

## Tags: #TX-ISO, #DB-INT
## Status: Accepted

### Context
Iterative ingestion of Many-to-Many (M:N) data was frequently failing due to IntegrityError (duplicate links) or ForeignKey violations. In a standard SQLAlchemy session, these failures "poisoned" the transaction, triggering a PendingRollbackError for all subsequent operations and forcing a total rollback of the batch.

### Decision
Implement session.begin_nested() (SQL Savepoints) around all junction table insertions and atomic entity flushes.
* **Batch Ingestors**: Catch IntegrityError within the savepoint to allow the loop to continue (idempotency).
* **Atomic Ingestors**: Use the savepoint to isolate failures, then raise a ValueError to abort the specific corrupted record without crashing the session state.

### Consequences
* **Requirement**: Direct session.execute() calls for junction links without a surrounding begin_nested() block are strictly forbidden.
* **Stability**: The system now survives "dirty" CSV data containing duplicate links.

#DB-INT	    Database Integrity (Constraints, FKs, Cascades)
#TX-ISO	    Transaction Isolation (Savepoints, Atomic Aborts)
#IN-SAN	    Input Sanitization (Enum mapping, string formatting)
#API-CON    Interface/API Contracts (Status dictionary validation)
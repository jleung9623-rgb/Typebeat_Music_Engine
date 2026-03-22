# Architectural Decision Record 0003 - Implementation of Alembic Version Control

## Tags: #DB-MIG, #SYS-ARCH
## Status: Accepted

### Context
Applying the schema changes from ADR-0001 without version control caused environment desynchronization. We require a migration tracker.

### Decision
Integrate Alembic for database migration tracking. Every alteration to `models.py` must generate a corresponding Alembic revision script.

### Consequences
* **Requirement**: Developers must run `alembic upgrade head` to synchronize their local database state expressions.
* **Constraint**: Manual `DROP TABLE` or `ALTER TABLE` commands via a database CLI are forbidden.
# Architectural Decision Record 0002 - Integration of SQLAlchemy ORM

## Tags: #DB-ARCH, #SYS-ARCH
## Status: Accepted

### Context
Following the M:N junction table refactor (ADR-0001), managing foreign key cascades and track-to-motif limits via raw SQL became computationally fragile and prone to injection. We require an ORM.

### Decision
Implement SQLAlchemy as the primary Object-Relational Mapper (ORM). All database entities (Artists, Tracks, Motifs) must inherit from a unified `DeclarativeBase`.

### Consequences
* **Requirement**: Database interactions must utilize SQLAlchemy ORM sessions or Core binary expressions. 
* **Constraint**: Hardcoded raw SQL strings are strictly forbidden outside of explicit migration scripts.
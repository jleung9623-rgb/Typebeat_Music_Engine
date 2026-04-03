# Architectural Decision Record 0001 - M:N Junction Table Refactor and Unique Constraints

## Module: models.py
## Tags: #DB-INT, #SYS-ARCH
## Status: Accepted

### Context
The initial database schema attempted to map multi-parent entities using flat columns, severely limiting the *Dynamic Library*. For example, a single Motif could not be dynamically assigned to multiple tracks, compromising the micro-timing and groove limits of the generation loop.

### Decision
Refactor all multi-directional relationships into explicit *Many-to-Many (M:N)* junction tables (e.g., `track_motif_map`, `artist_genre_map`).

* Apply a composite `UniqueConstraint` on the paired Foreign Keys in every junction table to mathematically guarantee that duplicate links cannot exist.

### Consequences
* **Requirement**: All entity associations must traverse their respective mapping tables.

* **Stability**: The generation matrix will no longer process mathematically redundant weights caused by duplicate relationship rows.
# Architectural Decision Record 0005 - SQL Database Faculty Designation

## Tags: #SYS-ARCH, #DATA-FLOW
## Status: Accepted

### Context
Treating all musical data equally resulted in volatile lifecycle overlaps. Immutable music theory rules were being managed in the same pipeline as highly volatile, user-generated Motif sequences.

### Decision
Enforce a strict conceptual and relational partition across the database schema:
1. **Static Library:** Immutable core logic (Chords, Scales).
2. **Macro-Level Constraints:** High-level grouping containers (Artists, Genres, Blueprints, Tracks).
3. **Dynamic Library:** Volatile, granular generated data (Motifs, Motif Notes, Transitions).

### Consequences
* **Requirement**: Foreign keys must respect the hierarchy. Dynamic Library entities can depend on Macro constraints, but Static Library entities must remain strictly independent.
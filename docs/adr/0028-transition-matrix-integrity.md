# Architectural Decision Record 0028 - Transition Matrix Integrity & Edge Generation

## Module: transitions_upload.py
## Tags: #GRAPH-LOGIC, #DATA-INTEGRITY, #MARKOV-MATRIX
## Status: Accepted

### Context
The Markov engine requires mathematical edges (*Transitions*) to navigate between nodes (*Motifs*). A mechanism was required to build these paths while explicitly preventing connections that violate the predefined `SongBlueprint` sequences.

### Decision
Implemented logic to automatically generate and constrain mathematical edges.

* **Heuristic Baseline**: Automatically generates a 1.0 heuristic baseline matrix of valid paths by reading blueprint block sequences.

* **Constrained Override**: A manual CSV override is authorized for probability tuning, but it is strictly constrained by a SQL validation query.

* **Zero-Trust Boundaries**: The script actively rejects any manually requested edge that attempts to execute structural defiance (e.g., linking a Chorus directly back to an Intro).

### Consequences
* **Stability**: Absolute structural integrity is guaranteed at the PostgreSQL database level.

* **Trade-offs**: The baseline algorithm handles the primary workload, and manual overrides are mechanically prevented from corrupting the sequence constraint, sacrificing absolute freedom for architectural safety.
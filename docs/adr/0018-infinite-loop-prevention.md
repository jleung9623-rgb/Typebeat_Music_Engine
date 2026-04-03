# Architectural Decision Record 0018 - Markov Matrix Infinite Loop Prevention

## Module: markov_engine.py
## Tags: #MARKOV, #FAULT-TOLERANCE
## Status: Accepted

### Context
The `generate_timeline` block relies on a `while current_beats < target_beats:` loop to fill the structural blueprints. If a motif is selected that has zero valid outgoing transitions in the transitions table, the select_motif query returns None. Without a safety check, the loop would infinitely attempt to calculate a duration for None and advance a frozen clock, causing a silent memory hang.

### Decision
Implement a strict safety halt constraint within the block generation loop.

* If `next_id` evaluates to *None*, the loop prints a dead-end warning and immediately executes a break command to terminate block generation.

### Consequences
* **Requirement**: Stress-test motif databases must be dense enough to provide valid transition weights, or blocks will consistently generate short of their target beat length.

* **Stability**: CPU lockups and infinite loops are mathematically impossible, even when navigating heavily sparse transition matrices.
# Architectural Decision Record 0032 - Context-Aware Markov Pathing

## Module: markov_engine.py
## Tags: #MARKOV-ENGINE, #GRAPH-TRAVERSAL, #RUNTIME-SAFETY
## Status: Accepted

### Context
During runtime, the Markov engine evaluates a node and selects an attached edge. If the engine read all available transitions blindly, it could theoretically select a path that derails the chronological progression of the track.

### Decision
Updated the `markov_engine.py` read-logic.

* **Dynamic Cross-Referencing**: The engine dynamically cross-references available transitions against the active SongBlueprint block.

* **Constrained Probability**: It physically isolates and calculates probabilities exclusively for paths that satisfy the current blueprint constraint.

### Consequences
* **Stability**: Enforces zero-trust boundary enforcement during runtime.

* **Impact**: Prevents premature block jumping and ensures the generative output strictly adheres to the uploaded song structure, acting as a secondary fail-safe against anomalous database edges.
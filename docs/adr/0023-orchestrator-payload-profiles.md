# Architectural Decision Record 0023 - Strict Dictionary Profiles for Orchestrator Payloads

## Module: main.py
## Tags: #DATA-INT, #PAYLOAD-CONSTRUCTION
## Status: Accepted

### Context
The user CLI input loop originally pushed raw string data into the track_requests array. When the payload was passed to the downstream worker (`transpose_motif`), the function attempted to execute a `.get()` call, assuming the payload items were dictionaries. This caused a fatal `AttributeError` during execution.

### Decision
Implement strict gatekeeper logic to enforce dictionary construction at the absolute point of ingestion.

* Wrap raw string inputs into *uniform dictionaries* (`{'track_name': track_input}`) before appending them to the request payload.

### Consequences
* **Requirement**: All inter-module payload transitions must utilize strictly typed dictionary objects, not raw strings or isolated primitives.

* **Stability**: Uniform data type expectations eliminate runtime attribute collisions across all worker modules.
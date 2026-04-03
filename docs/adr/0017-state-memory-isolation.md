# Architectural Decision Record 0017 - Markov State Memory Isolation

## Module: markov_engine.py
## Tags: #MARKOV, #STATE-MGMT, #POLYPHONY
## Status: Accepted

### Context
When iterating through the `generation_payload['tracks']` array, the system utilizes an `active_motif_id` to establish the transitional "from" state of the Markov chain. If this state memory is not purged between track iterations, the generator attempts to link the final motif of Track A (e.g., Bass) to the first motif of Track B (e.g., Piano), which causes an instant SQL lookup failure due to isolated Track-Motif mappings.

### Decision
Explicitly isolate the Markov state memory within the orchestrator loop.

* The `motif_id_temp` variable is reset to None at the absolute beginning of every instrument iteration inside `run_generator`.

### Consequences
* **Requirement**: Each track must independently seed its first motif using weighted randomness rather than relying on a transition from a previous instrument.

* **Stability**: Completely prevents cross-contamination of probability matrices across different MIDI channels.
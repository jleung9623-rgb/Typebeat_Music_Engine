# Architectural Decision Record 0038 - Continuous Temporal Variable and Rest Data Integration

## Module: engine/harmonic_analyzer.py, engine/markov_engine.py, engine/midi_builder.py
## Tags: #TEMPORAL-GEOMETRY, #GENERATIVE-LOOP, #STATE-SYNC
## Status: Accepted

### Context
The legacy generation loop and ingestion pipeline operated on a rigidly quantized grid. It actively dropped continuous spatial metrics (`micro_offset`) at rendering, erased human groove, and failed to account for leading/trailing silence (`phrase_latency`, `rest_duration`). This caused the discrete Markov Engine to miscalculate blueprint capacities, desynchronizing the Orchestrator's **global clock** and resulting in cascading polyphonic collisions where structural sections undercut physical audio execution.

### Decision
Re-engineered the ingestion and generative loops to operate on continuous temporal dimensions, synchronizing the mathematical state machine with physical audio reality.

* **Global Clock Synchronization**: Modified the orchestration loop to calculate absolute boundary terminations using phrase_latency + beat_position + duration, preventing the engine from triggering subsequent motifs while delayed payloads are still executing.

* **Markov Capacity Alignment**: Patched the discrete capacity logic to sum `phrase_latency` alongside base offsets and rest_duration, ensuring the sequence footprint perfectly mirrors the Orchestrator's continuous timeline.

* **Groove Preservation**: Integrated float-based `micro_offset` metrics directly into the absolute tick calculation during final .mid binary serialization, halting the violent mathematical erasure of human syncopation.

* **Schema Synchronization**: Executed a DDL alteration converting rest_suffix from Float to String(50) to securely map categorical pipeline flags (e.g., "NONE") without triggering fatal data type errors.

### Consequences
* **Temporal Integrity**: Continuous vector-based humanization metrics survive the complete generative loop and exist in the final rendered artifact.

* **Mathematical Dependency**: The architecture is now fundamentally reliant on continuous float mathematics for timing; any regression to discrete grid-snapping at the extraction phase will permanently break the global timeline synchronization.
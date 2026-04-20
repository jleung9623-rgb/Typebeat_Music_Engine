# Architectural Decision Record 0035 - Timeline Rectification via Offset Integration

## Module: main/main.py
## Tags: #ORCHESTRATOR, #TIMELINE-MATH, #MIDI-GENERATION
## Status: Accepted

### Context
The linear MIDI generation logic within the main orchestrator assumed static, grid-locked continuity. This ignored the asymmetrical motif lengths and structural whitespace calculations established upstream, leading to timeline collapse and polyrhythmic desynchronization during file compilation.

### Decision
Integrated the mathematical ingestion of both phrase latency and motif pivot offsets directly into the MIDI output generation loop.

* **Offset Math**: The orchestrator now properly incorporates `phrase_latency` and `motif_pivot_offset` sequentially to dictate *global clock advancement*.

### Consequences
* **Synchronization**: The global clock accurately advances based on physical offsets, successfully preserving the macro-grid and allowing for complex phrasing.

* **Dependency Risk**: The MIDI generator is now entirely dependent on the mathematical accuracy of the upstream extraction scripts. A single malformed offset value logged in the database will irreparably drift the entire track timeline.
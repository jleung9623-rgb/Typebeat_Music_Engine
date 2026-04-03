# Architectural Decision Record 0024 - Flat List Enforcement for Delta-Time Sequencing

## Module: main.py
## Tags: #DATA-INT, #MIDI-BUILD
## Status: Accepted

### Context
During the post-production rendering phase, appending individual track MIDI events to the `final_midi_data` array resulted in a 2D nested list structure ([[event1, event2], [event3]]). The binary MIDI builder (`midi_builder.py`) strictly requires a flat, 1D sequential list to calculate chronologically sorted delta-ticks. The nested list bypassed the sorting logic and triggered a fatal dimension mismatch crash.

### Decision
Enforce flat-list dimensioning during the transposition array merge.

* Replace the `.append()` method with `.extend()` when hydrating the `final_midi_data` array in the main orchestrator.

### Consequences
* **Requirement**: All modules returning MIDI event data must return flat arrays of dictionaries, which must be extended, never appended.

* **Stability**: Downstream chronological sorting and binary delta-tick calculations will successfully parse all events across all channels simultaneously.
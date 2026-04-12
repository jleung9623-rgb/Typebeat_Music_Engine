# Architectural Decision Record 0031 - Track-Level Transposition Logic

## Module: harmonic_analyzer.py
## Tags: #HARMONICS, #DATA-TRANSFORMATION, #POLYPHONY
## Status: Accepted

### Context
Extracted MIDI motifs hold static pitch values. To maintain harmonic cohesion across multiple polyphonic instruments, these static pitches must be dynamically shifted to match the master track environment.

### Decision
Implemented track-level transposition logic.

* **Root Isolation**: The algorithm isolates the musical root data of the selected motif.

* **Mathematical Offset**: Applies mathematical offsets to align the isolated data with the parent track's designated scale and octave modifiers.

### Consequences
* **Requirement**: Requires rigorous cache synchronization so the transposition math always references the most recent static chord definitions.

* **Stability**: Ensures phase and scale alignment across the entire generated arrangement.
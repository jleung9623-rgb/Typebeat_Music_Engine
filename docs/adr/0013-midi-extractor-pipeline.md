# Architectural Decision Record 0013 - MIDI Extractor Data Pipeline

## Module: midi_extractor.py
## Tags: #DATA-FLOW, #SYS-ARCH
## Status: Accepted

### Context
Raw MIDI files contain unstructured byte data. Feeding this directly into the generation matrix would bypass all relational constraints, genre weightings, and the `SectionClass` schema.

### Decision
Implement a unidirectional extraction pipeline in `midi_extractor.py` that parses raw MIDI files, isolates pitch/velocity/timing data, and strictly maps it to the `Motif` and `MotifNote` ORM entities prior to database insertion.

### Consequences
* **Constraint**: The Markov generator is strictly forbidden from reading raw `.mid` files. It may only read from the structured `Motifs` table.
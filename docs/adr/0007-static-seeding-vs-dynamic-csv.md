# Architectural Decision Record 0007 - Static Seeding vs. Dynamic CSV Uploads

## Module: harmonic_map.py, motifs_upload.py, metadata_sb_upload.py
## Tags: #DATA-FLOW, #SYS-ARCH
## Status: Accepted

### Context
Attempting to manage fundamental music theory data via CSV uploads introduced the risk of human formatting errors destroying the core harmonic logic of the generation engine.

### Decision
Differentiate ingestion methods based on data volatility:
* **Static Seeding**: Use hardcoded Python dictionaries via internal class methods (e.g., `HarmonicMap.seed_basic_chords()`) for absolute, mathematically proven musical data.
* **Dynamic CSV**: Restrict file-based uploads exclusively to user-defined metadata and MIDI-extracted motifs.

### Consequences
* **Requirement**: Users cannot upload custom scales or base chords via CSV. Harmonic mapping remains under strict programmatic control.
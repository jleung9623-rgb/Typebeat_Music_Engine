# Architectural Decision Record 0010 - Motif Upload Chord Blindness Guardrail

## Module: motif_uploads.py
## Tags: #ERR-HDL, #DB-INT
## Status: Accepted

### Context
During bulk Motif ingestion, assigning a `chord_id` that had not yet been seeded into the Static Library caused a silent Foreign Key failure. This wasted computational cycles as the script parsed the entire CSV only to fatally crash during the final `session.commit()`.

### Decision
Implement explicit pre-validation for chord dependencies. The ingestor must query the Static Library for the `chord_id` during the parsing loop. If it does not exist, explicitly raise a `ValueError` to halt the specific motif processing immediately.

### Consequences
* **Requirement**: The Static Library must be fully seeded before the Dynamic Library can be populated.

* **Stability**: Prevents "blind" data ingestion for non-existent chords into motif-level data.
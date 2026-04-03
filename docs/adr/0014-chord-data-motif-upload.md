# Architectural Decision Record 0014 - Harmonic Resolution via In-Memory Caching During Motif Ingestion

## Module: motifs_upload.py
## Tags: #DATA-FLOW, #SYS-ARCH
## Status: Accepted

### Context
Motif uploads originate from flat CSV files containing only raw performance data (`pitch_value`, `beat_position`, `duration`). To maintain strict relational normalization and support the downstream mathematical generation engine, these concurrent raw pitches must be mapped to existing `chord_id` records in the database.

### Decision
* **Pre-emptive Eager Loading**: Upon instantiation of the `CSVUploader`, open a localized session to execute a single, eager-loaded (`joinedload`) query of all verified Chord and ChordNote records.

* **O(1) Memory Cache**: Construct a static RAM dictionary. Convert the absolute MIDI integers into a mathematically normalized signature: (`root_pitch_class, tuple(intervals)`). Use this signature as the composite key, mapping directly to the `chord.id` value.

* **Dynamic Foreign Key Assignment**: During the Pandas `DataFrame` iteration, group concurrent notes by beat_position, calculate their mathematical signature on the fly, and execute an O(1) dictionary lookup. Dynamically assign the resolved `chord_id` as a `ForeignKey` on the `MotifNote` object prior to executing the `session.add_all()` bulk insert.

### Consequences
* **Performance**: Ingestion latency is strictly bound to file I/O and bulk insert speeds, entirely bypassing the N+1 query flaw.

* **Stability**: Database normalization is perfectly preserved. The MotifNote table remains lightweight, acting only as a performance instance pointing back to the heavy, centralized harmonic library.

* **Constraint**: The cache is statically loaded at runtime. If the database's Chord table is modified by another process during an active ingestion lifecycle, the script will not recognize the new chords.
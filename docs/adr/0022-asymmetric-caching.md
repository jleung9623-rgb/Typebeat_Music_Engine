# Architectural Decision Record 0022 - Asymmetric Caching for Dynamic Motif Ingestion

## Module: upload_interface.py
## Tags: #STATE-MGMT, #INGESTION
## Status: Accepted

### Context
The *Motif Uploader (DynamicLibrary)* hashes raw MIDI notes against known interval tuples to assign a chord_id. To optimize this, the uploader caches the static SQL chord database into RAM upon initialization. Booting the upload interface on a fresh, empty schema resulted in an empty RAM cache. When the database was subsequently seeded, the RAM cache remained empty, causing all motif uploads to fail because the uploader could not recognize the newly generated chords.

### Decision
Bind the RAM cache rebuild directly to the SQL seeding event within the CLI switchboard.

* Explicitly execute `d_lib.chord_cache = d_lib.build_chord_cache()` immediately after Choice 1 (`seed_basic_chords`) completes.

### Consequences
* **Requirement**: Any function that modifies the static foundational library must manually trigger a cache refresh in the dynamic ingestor.

* **Stability**: Prevents cache desynchronization, mathematically guaranteeing that incoming motifs always hash against the live state of the SQL database.
# Architectural Decision Record 0016 - True Polyphonic Markov Matrixing

## Module: markov_engine.py
## Tags: #SYS-ARCH, #MARKOV, #POLYPHONY
## Status: Accepted

### Context
The generator originally hard-coded the payload parameter to track index [0]. This forced the engine to calculate transitions for only one instrument and duplicate that monophonic timeline across all requested MIDI channels. Upon patching the engine to return a multi-threaded polyphonic dictionary ({track_id: [motif_ids]}), the orchestrator attempted to pass the entire dictionary to the transposer, causing Python to iterate over dictionary keys instead of Motif IDs and instantly crash the database query.

### Decision
Refactor the Markov Engine to execute independent probability matrices for every requested track and return a stateful dictionary.

* In the orchestrator, explicitly unpack the dictionary using `master_timeline`.`get(current_track_id)` to isolate the flat list of Motif IDs before passing it to the harmonic transposer.

### Consequences
* **Requirement**: The `transpose_motif` function must only ever receive a 1D list of integer IDs.

* **Stability**: The software pipeline mathematically supports true polyphonic orchestration, allowing every instrument to traverse its own independent transition matrix.
# Architectural Decision Record 0021 - Absolute to Delta Time Chronological Sorting

## Module: midi_builder.py
## Tags: #MIDI-BUILD, #TEMPORAL-MATH
## Status: Accepted

### Context
The `mido` library and binary .mid formats require *Delta Time* (ticks elapsed since the previous event on the track). However, the `harmonic_analyzer` outputs events in Absolute Time. If absolute events are converted to delta ticks without sorting, overlapping notes (like chords) produce negative time values, which instantly corrupts the binary file output.

### Decision
Pool, sort, and sequence all events chronologically before binary calculation.

* Convert *Absolute Beats* to *Absolute Ticks* for both note_on and note_off events.
* Pool all events into a flat midi_events array and sort chronologically via `midi_events.sort(key=lambda x: x['time'])`.
* Iterate through the sorted array to calculate `delta_ticks = ev['time'] - current_ticks`.

### Consequences
* **Requirement**: No module preceding midi_builder.py is permitted to calculate Delta Time.

* **Stability**: Mathematically seals the binary compilation. Polyphonic overlap, simultaneous chord structures, and dense micro-timing offsets are rendered flawlessly without negative-tick crashes.
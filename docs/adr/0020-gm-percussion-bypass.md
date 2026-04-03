# Architectural Decision Record 0020 - General MIDI Percussion Bypass (Channel 10)

## Module: harmonic_analyzer.py
## Tags: #MIDI-BUILD, #HARMONICS
## Status: Accepted

### Context
The `harmonic_analyzer.py` calculates transposition by calculating the relative intervals of a motif note and mapping them onto a target scale. Applying this logic indiscriminately corrupts percussion tracks. A kick drum (Pitch 36) mapped to a C Minor scale might be transposed to Pitch 38 (Snare Drum), destroying the rhythmic structure.

### Decision
Implement a strict structural bypass for rhythmic instruments based on standard `General MIDI (GM)` specifications.

* If `midi_channel == 10`, the transpose_motif function skips the `map_pitch_to_scale` function entirely and directly applies `note.pitch_value` to the final output.

### Consequences
* **Requirement**: All drum and percussion tracks uploaded to the SQL schema must strictly be mapped to midi_channel = 10 during ingestion.

* **Stability**: Preserves the structural integrity of unpitched percussion sequences while ensuring strict harmonic cohesion for melodic tracks.
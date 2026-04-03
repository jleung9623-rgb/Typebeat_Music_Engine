# Architectural Decision Record 0019 - Absolute Temporal Mapping via Global Clock

## Module: harmonic_analyzer.py
## Tags: #SYS-ARCH, #TEMPORAL-MATH
## Status: Accepted

### Context
Raw Motifs stored in the database natively start at beat_position = 0.0. Without macro-arrangement mathematics, the transposer assigned all motifs to beat 0.0, causing an "Absolute Time Collapse" where the entire 3-minute composition played simultaneously in the first 2 seconds. Furthermore, advancing a global clock inside the inner note loop erroneously arpeggiated simultaneous chords, destroying micro-timing.

### Decision
Introduce a `current_song_beat` global clock in the harmonic analyzer to establish a continuous temporal ruler.

* Calculate absolute note time via `absolute_beat = current_song_beat + note.beat_position`.
* Outdent the clock incrementation (`current_song_beat += max_motif_beat`) to execute exactly once per motif block, strictly outside the inner note loop.

### Consequences
* **Requirement**: The `harmonic_analyzer` is solely responsible for Absolute Time mapping, while `midi_builder` handles Delta Time binary conversion.

* **Stability**: The engine perfectly preserves micro-timing (simultaneous chord structures) while successfully stitching the macro-arrangement timeline into a linear sequence.
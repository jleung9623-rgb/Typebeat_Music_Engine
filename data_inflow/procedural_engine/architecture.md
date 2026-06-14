procedural_engine/
│
├── core_generator.py (The Orchestrator: Manages the Bounded Matrix & Execution Pipeline)
│
├── harmony_domain/ (Calculates Vertical Pitch - mutates `pitch_value` in stateless arrays)
│   ├── base_harmony.py (Abstract Contract for Harmony Modules)
│   ├── modal_interchange.py (Calculates parallel minor triad substitutions)
│   ├── trap_voicings.py (Enforces wide bass intervals and tight upper clusters)
│   └── voice_leading.py (Calculates shortest vertical distance between sequential chord inversions)
│
├── rhythmic_domain/ (Calculates Macro-Timing - outputs base `List[Dict]`)
│   ├── base_rhythmic.py (Abstract Contract for Rhythmic Modules)
│   └── quantized_grid.py (Projects stateless pitch arrays onto a universal temporal grid)
│
├── melodic_domain/ (Calculates Horizontal Pitch - mutates `pitch_value` across time)
│   ├── base_melodic.py (Abstract Contract for Melodic Modules)
│   └── passing_tones.py (Extracts monophonic anchors and injects diatonic bridging notes)
│
├── articulation_domain/ (Calculates Micro-Timing - mutates `micro_offset` & `duration`)
│   ├── base_articulation.py (Abstract Contract for Articulation Modules)
│   ├── dilla_swing.py (Drags off-beat 16th notes while enforcing a ±0.125 database limit)
│   └── lazy_tail.py (Identifies phrase-terminating notes and extends duration)
│
└── velocity_domain/ (Calculates Dynamics - injects the `velocity` key)
    └── velocity_humanizer.py (Hybrid matrix: Rhythmic hierarchy + frequency bracketing)
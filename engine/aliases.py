"""
Static configuration data and deterministic routing dictionaries.
Quarantined from the main orchestrator to enforce separation of concerns.
"""

SCALE_ALIASES = {
    "major": "Major (Ionian)",
    "ionian": "Major (Ionian)",
    "major (ionian)": "Major (Ionian)",
    "minor": "Natural Minor (Aeolian)",
    "aeolian": "Natural Minor (Aeolian)",
    "natural minor": "Natural Minor (Aeolian)",
    "natural minor (aeolian)": "Natural Minor (Aeolian)",
    "harmonic minor": "Harmonic Minor",
    "melodic minor": "Melodic Minor",
    "major pentatonic": "Major Pentatonic",
    "minor pentatonic": "Minor Pentatonic",
    "blues": "Blues Scale",
    "blues scale": "Blues Scale",
    "dorian": "Dorian",
    "phrygian": "Phrygian",
    "lydian": "Lydian",
    "mixolydian": "Mixolydian",
    "locrian": "Locrian",
    "chromatic": "Chromatic",
    "whole tone": "Whole Tone",
    "diminished": "Diminished (W-H)",
    "harmonic major": "Harmonic Major",
    "hungarian minor": "Hungarian Minor"
}

ROOT_ALIASES = {
    "c": 60, "b#": 60,
    "c#": 61, "db": 61,
    "d": 62,
    "d#": 63, "eb": 63,
    "e": 64, "fb": 64,
    "f": 65, "e#": 65,
    "f#": 66, "gb": 66,
    "g": 67,
    "g#": 68, "ab": 68,
    "a": 69,
    "a#": 70, "bb": 70,
    "b": 71, "cb": 71
}
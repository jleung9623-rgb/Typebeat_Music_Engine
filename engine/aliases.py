
from database.models import SectionClass
from database.models import TrackClass

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

BLUEPRINT_BLOCK_LENGTHS = {
    SectionClass.OPENING: 16.0,
    SectionClass.VERSE: 16.0,
    SectionClass.VERSE_B: 16.0,
    SectionClass.PRE_CHORUS: 16.0,
    SectionClass.CHORUS: 16.0,
    SectionClass.CHORUS_B: 16.0,
    SectionClass.CHORUS_FINAL: 32.0,
    SectionClass.BUILD: 16.0,
    SectionClass.DE_ESCALATION: 8.0,
    SectionClass.BRIDGE: 16.0,
    SectionClass.ENTROPIC: 16.0,
    SectionClass.REST: 8.0,
    SectionClass.OUTRO: 16.0
}

# Maps Looperman's Timbre Categories to Typebeat's Functional Enums
LOOPERMAN_TRACK_ROUTING = {
    # Bass Frequencies
    "bass": TrackClass.BASS,
    "bass guitar": TrackClass.BASS,
    "bass synth": TrackClass.BASS,
    "bass wobble": TrackClass.BASS,

    # Percussive Elements
    "beatbox": TrackClass.PERCUSSION,
    "drum": TrackClass.PERCUSSION,
    "groove": TrackClass.PERCUSSION,
    "percussion": TrackClass.PERCUSSION,
    "tabla": TrackClass.PERCUSSION,

    # Harmonic / Atmospheric Pads
    "choir": TrackClass.PAD_ATMOSPHERE,
    "didgeridoo": TrackClass.PAD_ATMOSPHERE,
    "orchestral": TrackClass.PAD_ATMOSPHERE,
    "organ": TrackClass.PAD_ATMOSPHERE,
    "pad": TrackClass.PAD_ATMOSPHERE,
    "soundscapes": TrackClass.PAD_ATMOSPHERE,
    "strings": TrackClass.PAD_ATMOSPHERE,

    # FX & Incidentals
    "fx": TrackClass.FX,
    "scratch": TrackClass.FX,

    # Melodic Leads (The Default Fallback for Pitched Instruments)
    "accordion": TrackClass.MELODIC_LEAD,
    "arpeggio": TrackClass.MELODIC_LEAD,
    "bagpipe": TrackClass.MELODIC_LEAD,
    "banjo": TrackClass.MELODIC_LEAD,
    "bells": TrackClass.MELODIC_LEAD,
    "brass": TrackClass.MELODIC_LEAD,
    "clarinet": TrackClass.MELODIC_LEAD,
    "flute": TrackClass.MELODIC_LEAD,
    "guitar acoustic": TrackClass.MELODIC_LEAD,
    "guitar electric": TrackClass.MELODIC_LEAD,
    "harmonica": TrackClass.MELODIC_LEAD,
    "harp": TrackClass.MELODIC_LEAD,
    "harpsichord": TrackClass.MELODIC_LEAD,
    "mandolin": TrackClass.MELODIC_LEAD,
    "piano": TrackClass.MELODIC_LEAD,
    "rhodes piano": TrackClass.MELODIC_LEAD,
    "sitar": TrackClass.MELODIC_LEAD,
    "synth": TrackClass.MELODIC_LEAD,
    "ukulele": TrackClass.MELODIC_LEAD,
    "violin": TrackClass.MELODIC_LEAD,
    "vocal": TrackClass.MELODIC_LEAD,
    "woodwind": TrackClass.MELODIC_LEAD
}
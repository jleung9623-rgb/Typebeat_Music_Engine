import pytest
import os
from mido import MidiFile
from engine.midi_builder import sanitize_filename, build_midi_file

def test_sanitize_filename():
    """Verifies regex filters illegal filesystem characters while preserving valid ones."""

    raw_filename = "Typebeat_Song<>?:\"|*\\/123!"
    clean_filename = sanitize_filename(raw_filename)

    assert clean_filename == "Typebeat_Song123", f"CRITICAL: Regex sanitiation failed. Got {clean_filename} instead."

def test_absolute_to_delta_sorting(tmp_path):
    """
    Verifies Logic from ADR-0021: The engine must chronologically sort absolute beats
    and calculate non-negative delta ticks, especially for simultaneous chord notes.
    """

    # Constructs an unordered polyphonic payload
    global_midi_data = [
        {'midi_channel': 1, 'pitch': 60, 'beat_position': 2.0, 'duration': 1.0}, # Occurs later (Beat 2)
        {'midi_channel': 1, 'pitch': 64, 'beat_position': 0.0, 'duration': 1.0}, # Chord Note 1 (Beat 0)
        {'midi_channel': 1, 'pitch': 67, 'beat_position': 0.0, 'duration': 1.0}  # Chord Note 2 (Beat 0)
    ]

    metadata = {'default_tempo': 120}
    output_dir = str(tmp_path)
    file_name = "test_delta_sorting"

    # Executes the MIDI file building process
    file_path, final_name = build_midi_file(global_midi_data, file_name, metadata, output_dir)

    assert os.path.exists(file_path), "CRITICAL: MIDI file was not generated in temporary directory."

    # Binary Verification
    mid = MidiFile(file_path)

    track = mid.tracks[1]

    # Isolate not events from other meta messages to verify correct chronological order and delta tick calculation
    note_events = [msg for msg in track if msg.type in ('note_on', 'note_off')]

    assert note_events[0].time == 0, "CRITICAL: First event must start at delta 0."
    assert note_events[1].time == 0, "CRITICAL: Simultaneous chord note(s) must have delta 0."

    for msg in note_events:
        assert msg.time >= 0, f"CRITICAL: Negative delta time calculated: {msg.time}"
import pytest
from unittest.mock import Mock, MagicMock
from database.models import Motif, MotifNote
from engine.harmonic_analyzer import map_pitch_to_scale, transpose_motif

def test_standard_major_to_minor_transposition():
    """Verifies that an E-natural (Major 3rd) in C major transposes to an F-natural (Minor 3rd) in D minor."""

    raw_pitch = 64      # E4 (Major 3rd in C major)
    target_root = 62    # D4 (Root of D minor)

    target_intervals = [2, 1, 2, 2, 1, 2, 2]  # D minor scale intervals (W, H, W, W, H, W, W)

    transposed_pitch = map_pitch_to_scale(raw_pitch, target_root, target_intervals)

    assert transposed_pitch == 65, f"CRITICAL: Expected 65 (F4), got {transposed_pitch} instead."

def test_octave_shift_preservation():
    """Verifies that the algorithm correctly calculates and maintains octave heights above Middle C."""

    raw_pitch = 79      # G5 (Perfect 5th, one octave above Middle C)
    target_root = 60    # C4 (No root shift, testing only the interval and octave math)

    target_intervals = [2, 2, 1, 2, 2, 2, 1]  # C major scale intervals

    transposed_pitch = map_pitch_to_scale(raw_pitch, target_root, target_intervals)

    assert transposed_pitch == 79, f"CRITICAL: Expected 79 (G5), got {transposed_pitch} instead."

def test_out_of_scale_accidentals():
    """Verifies the fallback logic when a raw pitch contains an accidental not in the default scale."""

    raw_pitch = 61      # C#4 (Accidental not in C major)
    target_root = 62    # D4 (Root of D major)

    target_intervals = [2, 2, 1, 2, 2, 2, 1]  # D major scale intervals

    transposed_pitch = map_pitch_to_scale(raw_pitch, target_root, target_intervals)

    assert transposed_pitch == 63, f"CRITICAL: Expected 63 (D#4), got {transposed_pitch} instead."

def test_transpose_motif_orchestration():
    """Verifies the integration of absolute temporal mapping, octave shifting, and the GM percussion bypass."""

    mock_session = MagicMock()

    # Mock motif to test phrase_latency calculation
    mock_motif = Mock()
    mock_motif.phrase_latency = 1.0

    # Mock motif note to test duration and absolute temporal mapping
    mock_note = Mock()
    mock_note.pitch_value = 60 # C4
    mock_note.beat_position = 0.0
    mock_note.duration = 4.0
    mock_note.micro_offset = 0.0

    # Mock switchboard routing logic to return the appropriate motif and motif notes based on the query
    def mock_query_side_effect(model_or_column):
        query_mock = MagicMock()
        if model_or_column is Motif:
            query_mock.filter.return_value.first.return_value = mock_motif
        elif model_or_column is MotifNote:
            query_mock.filter.return_value.all.return_value = [mock_note]
        else:
            # Assumes any other query is the track_motif_map octave_shift scalar
            query_mock.filter.return_value.scalar.return_value = 1 # Forces a +1 octave_shift (12 semitones)
        return query_mock
    
    mock_session.query.side_effect = mock_query_side_effect

    master_timeline = [101, 102]

    track_melodic = {
        'track_id': 1,
        'midi_channel': 1,
        'default_root_note': 60,
        'intervals': [2, 2, 1, 2, 2, 2, 1]
    }

    track_percussion = {
        'track_id': 2,
        'midi_channel': 10, # GM Standard Drum Channel
        'default_root_note': 60,
        'intervals': [2, 2, 1, 2, 2, 2, 1]
    }

    melodic_data = transpose_motif(mock_session, master_timeline, track_melodic)

    assert len(melodic_data) == 2, "CRITICAL: Should return exactly 2 MIDI events."
    assert melodic_data[0]['pitch'] == 72, f"CRITICAL: Expected Pitch value of 72, got {melodic_data[0]['pitch']} instead."
    assert melodic_data[0]['beat_position'] == 1.0, "CRITICAL: Absolute time calculation failed."
    assert melodic_data[1]['beat_position'] == 5.0, "CRITICAL: Global clock advancement failed."

    percussion_data = transpose_motif(mock_session, master_timeline, track_percussion)

    assert percussion_data[0]['pitch'] == 60, "CRITICAL: Percussion bypass failed. Pitch was erroneously altered."
import pytest
from unittest.mock import Mock, patch
from database.models import SectionClass
from engine.markov_engine import run_generator

@pytest.fixture
def mock_db_session():
    """Provides an isolation mock session to bypass actual SQL execution."""
    return Mock()

@pytest.fixture
def valid_payload():
    """Provides a template static payload for the engine to process."""
    return {
        'metadata': {
            'artist_name': 'Test Artist',
            'genre_name': 'Techno',
            'default_tempo': 120,
            'time_signature': '4/4',
            'song_length': 80
        },
        'tracks': [
            {
                'track_id': 1, 
                'track_name': 'PERCUSSION', 
                'midi_channel': 10,
                'scale_name': 'Chromatic', 
                'default_root_note': 60,
                'intervals': '1,1,1,1,1,1,1,1,1,1,1,1'
            },
            {
                'track_id': 2, 
                'track_name': 'BASS', 
                'midi_channel': 2,
                'scale_name': 'Minor', 
                'default_root_note': 69,
                'intervals': '2,1,2,2,1,2,2'
            }
        ],
        'blueprints': [
            {
                'block_position': 1,
                'block_class': SectionClass.OPENING
            },
            {
                'block_position': 2,
                'block_class': SectionClass.VERSE
            }
        ]
    }

@patch('engine.markov_engine.get_motif_duration')
@patch('engine.markov_engine.select_motif')
def test_generator_valid_execution(mock_select_motif, mock_get_duration, mock_db_session, valid_payload):
    """Verifies the engine returns a correctly formatted dictionary keyed by track_id"""
    mock_select_motif.side_effect = [101, 102, 103, 104, 201, 202, 203, 204]
    mock_get_duration.return_value = 8.0

    timeline = run_generator(mock_db_session, valid_payload)

    assert isinstance(timeline, dict), "CRITICAL: Engine must return a dictionary."
    assert 1 in timeline, "CRITICAL: Missing Percussion track_id key."
    assert 2 in timeline, "CRITICAL: Missing Bass track_id key."
    assert isinstance(timeline[1], list), "CRITICAL: Track timeline must be a list of events."

    assert len(timeline[1]) == 4, "CRITICAL: Track 1 timeline length calculation failed."
    assert len(timeline[2]) == 4, "CRITICAL: Track 2 timeline length calculation failed."

@patch('engine.markov_engine.get_motif_duration')
@patch('engine.markov_engine.select_motif')
def test_generator_empty_tracks(mock_select_motif, mock_get_duration, mock_db_session, valid_payload):
    """Verifies engine handles an empty track array without throwing a NoneType error."""
    mock_select_motif.side_effect = [101, 102, 103, 104, 201, 202, 203, 204]
    mock_get_duration.return_value = 8.0

    valid_payload['tracks'] = []

    timeline = run_generator(mock_db_session, valid_payload)

    assert isinstance(timeline, dict), "CRITICAL: Engine must return a dictionary even if empty."
    assert len(timeline) == 0, "CRITICAL: Timeline should be empty when no tracks are requested."

@patch('engine.markov_engine.get_motif_duration')
@patch('engine.markov_engine.select_motif')
def test_generator_missing_blueprint(mock_select_motif, mock_get_duration, mock_db_session, valid_payload):
    """Verifies engine behavior when a track is requested but the genre blueprint is missing."""
    mock_select_motif.side_effect = [101, 102, 103, 104, 201, 202, 203, 204]
    mock_get_duration.return_value = 8.0
    
    valid_payload['blueprints'] = []

    timeline = run_generator(mock_db_session, valid_payload)
    
    assert 1 in timeline, "CRITICAL: Track 1 key should exist even if blueprint generation is skipped"
    assert len(timeline[1]) == 0, "CRITICAL: Track 1 timeline must be exactly 0."
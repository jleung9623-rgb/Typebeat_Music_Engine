from database.models import Artist, Track, Scale, track_scale_map, SongBlueprint, Genre, genre_blueprint_map
import random

def fetch_artist(session, artist_name=None):
    """Fetches the composition's artist based on controller input or default values"""

    # Fetches full list of artists from SQL database
    artist_list = session.query(Artist)

    # If artist name exists (From user input), selects it. Otherwise, selects a random artist from the entire list
    if artist_name:
        return artist_list.filter(Artist.artist_name == artist_name).first()
    
    print(f"WARNING: Artist '{artist_name}' not found. Using random available artist.")

    valid_artists = artist_list.all()
    return random.choice(valid_artists) if valid_artists else None
    
def fetch_genre(session, genre_name=None):
    """Fetches the composition's genre based on controller input or default values"""

    # Fetches full list of genres from SQL database
    genre_list = session.query(Genre)

    # If genre name exists (From user input), selects it. Otherwise, selects a random genre from the entire list
    if genre_name:
        return genre_list.filter(Genre.genre_name == genre_name).first()
    
    print(f"WARNING: Genre '{genre_name}' not found. Using random available genre.")
    
    valid_genres = genre_list.all()
    return random.choice(valid_genres) if valid_genres else None

def build_metadata_profile(session, artist_requests, genre_requests, song_length=0):
    """Uses the data collected from metadata helper functions to build the selected metadata profile."""
    
    # Fetches artist and genre metadata
    artist = fetch_artist(session, artist_requests)
    genre = fetch_genre(session, genre_requests)

    # Build final metadata profile before returning the output. Default values included in case neither artist nor genre exist
    final_metadata_profile = {
        'artist_name': artist.artist_name if artist else "Unknown Artist",
        'genre_name': genre.genre_name if genre else "Unknown Genre",
        'default_tempo': genre.default_tempo if genre else 120,
        'time_signature': genre.time_signature if genre else '4/4',
        'song_length': song_length
    }

    return final_metadata_profile

def fetch_track(session, track_name=None):
    """Fetches a Track object based on controller input or default fallback"""

    # Fetches full list of tracks from SQL database
    track_list = session.query(Track)

    # If track name exists (From user input), selects it. Otherwise uses the first available option 
    if track_name:
        return track_list.filter(Track.track_name == track_name).first()
    else:
        return track_list.first()


def fetch_track_scale(session, track_id, scale_name=None):
    """Fetches the root note and scale semitone intervals assigned to a specific track."""

    # Fetches list of scales based on eligible tracks (From 'unpack_track_library()')
    scale_list = session.query(Scale).join(track_scale_map).filter(track_scale_map.c.track_id == track_id)

    # If scale name exists, selects it. Otherwise, selects a random scale from the entire list
    if scale_name:
        return scale_list.filter(Scale.scale_name == scale_name).first()

    # Uses the corresponding junction table column to find default scale for designated track, selecting it if it exists
    default_scale = scale_list.filter(track_scale_map.c.is_default == True).first()

    if default_scale:
        return default_scale

    # If no default scale is found for track, selects a random scale
    print(f"WARNING: No default scale assigned to track_id {track_id}. Using random available scale.")
    
    valid_scales = scale_list.all()
    return random.choice(valid_scales) if valid_scales else None


def build_track_profile(session, track_requests):
    """Builds the composition's selected track list and corresponding starting pitches."""

    # Initializes list for track profile output
    final_track_profile = []
    
    for request in track_requests:
        # Fetches track based on either user input or default option
        track = fetch_track(session, request.get('track_name'))

        if not track:
            return None
        
        # Fetches scale for designated track
        scale = fetch_track_scale(session, track.id, request.get('scale_name'))

        if not scale:
            return None
        
        # Parses the string of the scale intervals, removing the commas and whitespace before converting them to integers. If the string is not properly formatted, raises an error.
        try:
            parsed_intervals = [int(step.strip()) for step in scale.intervals.split(',')]
        except Exception as e:
            raise ValueError(f"CRITICAL: Failed to parse interval string '{scale.intervals}' for track '{track.track_name}': {e}")

        # Builds the final track profile before returning the output
        final_track_profile.append({
            'track_id': track.id,
            'track_name': track.track_name,
            'midi_channel': track.midi_channel,
            'patch_number': track.patch_number,
            'track_motif_limit': track.track_motif_limit,
            'scale_id': scale.id,
            'scale_name': scale.scale_name,
            'default_root_note': request.get('root_override') or scale.default_root_note,
            'intervals': parsed_intervals
        })

    return final_track_profile


def fetch_blueprints(session, genre_name=None):
    """Fetches the composition's song structure based on designated genre."""

    # Fetches list of all blueprint blocks ordered by song structure position
    blueprint_list = (
        session.query(SongBlueprint)
        .join(genre_blueprint_map)
        .join(Genre)
        .order_by(SongBlueprint.block_position)
    )

    # If genre name exists (From user input), selects only the blocks under matching genre and returns them as a list
    if genre_name:
        selected_blueprint = blueprint_list.filter(Genre.genre_name == genre_name).all()

        if selected_blueprint:
            return selected_blueprint
        
        print(f"WARNING: No blueprint found for genre '{genre_name}'.")
    
    # If no blueprint is found for user's genre input, selects the first available genre as a default
    print("Using default available blueprint.")

    default_genre = session.query(Genre).first()

    if default_genre:
        return blueprint_list.filter(Genre.id == default_genre.id).all()
    
    return []


def build_blueprint_profile(session, genre_name=None):
    """Builds the composition's song structure by creating a data profile for each block."""

    # Fetches list of blueprint blocks associated with the designated genre
    blueprint_blocks = fetch_blueprints(session, genre_name)

    if not blueprint_blocks:
        return None

    # Initializes list for final blueprint output
    final_blueprint_profile = []

    # Builds the final profile for each block, before adding it to the final blueprint output list
    for block in blueprint_blocks:
        final_blueprint_profile.append({
            'block_position': block.block_position,
            'block_class': block.block_class,
        })

    return final_blueprint_profile
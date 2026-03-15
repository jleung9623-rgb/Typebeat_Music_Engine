import re
import datetime
import os
from database import DatabaseManager
from engine import MusicEngine
from music21 import midi

def sanitize_filename(name):
    """Filters any ineligible characters from filename input to prevent file system errors; allows only letters, numbers, dashes, underscores, and periods"""

    return re.sub(r'(?u)[^-\w.]', '', name) # Regex expression to filter any other exceptional character besides '-\w'


def save_version(score, db_save_state: DatabaseManager, save_name="typebeat"):
    """Saves the generated score to a MIDI file with a timestamped filename; includes error handling for file writing issues and unexpected exceptions"""
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")   # Generates a timestamp in the format YYYYMMDD_HHMMSS for iterative purposes
        file_name = f"{sanitize_filename(save_name)}_{timestamp}.mid"    # Runs save file through sanitization function to ensure it's a valid filename; appends timestamp for versioning and uniqueness
        file_path = os.path.abspath(file_name)

        # Translates Music21 score object into MIDI file format; opens MIDI file and writes data to it before closing
        midi_file = midi.translate.streamToMidiFile(score)      
        midi_file.open(file_name, 'wb')                         # Write binary mode to preserve current state of data
        midi_file.write()                                       
        midi_file.close()                                       # Ensures data is saved properly and resources are released
        
        print(f"--- SUCCESS: Created {file_name} ---")

        db_save_state.save_composition_record(file_name, file_path) # Logs the new composition into the SQL database to maintain a permanent history of generated files.
    except IOError as write_error:
        print(f"--- ERROR: Could not write file. {write_error} ---") # Catches file writing errors such as permission issues, disk space problems, or invalid filenames
    except Exception as system_error:
        print(f"--- UNEXPECTED ERROR: {system_error} ---") # Catches any other unforeseen exceptions


def main():
    """Main execution flow: Orchestrates the generation of a full-length composition by iterating through the song blueprint and applying track-specific motifs."""
    
    db = DatabaseManager() # Database initialization
    preferences = db.fetch_user_preferences() # Fetch set of user preferences from SQL database

    if not preferences:
        print("ERROR: Could not load preferences.")
        exit() # Exits program if user preferences not found

    # Song data initialization - Assigns data for current genre, length of song motif blocks
    GENRE = preferences.get('active_genre', 'Pop-Punk')
    GENRE_ID = 1
    SCORE_BLOCKS = int(str(preferences.get('song_length_blocks', 4)))

    print(f"--- Active Genre set to {GENRE} | Number of Song Blocks set to {SCORE_BLOCKS} ---")

    # SQL Fetch Commands - Collects data from SQL database
    track_rows = db.fetch_track_data(GENRE)
    engine = MusicEngine()
    engine.import_user_preferences(preferences)
    engine.initialize_tracks(track_rows, db)

    # Generates a Music21 score using the blueprints and data provided from the SQL database
    engine.generate_song(db, GENRE_ID, track_rows)
    
    # Finalization and Saving - Saves the generated MIDI file using a user-input name before closing the database
    save_name = input("Save file as: ")
    if not save_name:
        save_name = "typebeat_default" # Safety fallback if the user only types in symbols

    print("--- Finalizing Score Structure ---")

    save_version(engine.score, db, save_name) # Saves generated score

    db.close()

if __name__ == "__main__":
    main()
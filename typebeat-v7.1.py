import re
import datetime
import os
from database import DatabaseManager
from engine import MusicEngine
from music21 import midi

# Filters any ineligible characters from filename input to prevent file system errors; allows only letters, numbers, dashes, underscores, and periods
def sanitize_filename(name):
    return re.sub(r'(?u)[^-\w.]', '', name)


# Saves the generated score to a MIDI file with a timestamped filename; includes error handling for file writing issues and unexpected exceptions
def save_version(score, db_save_state: DatabaseManager, save_name="typebeat"):
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

        db_save_state.save_composition_record(file_name, file_path)
    except IOError as write_error:
        print(f"--- ERROR: Could not write file. {write_error} ---") # Catches file writing errors such as permission issues, disk space problems, or invalid filenames
    except Exception as system_error:
        print(f"--- UNEXPECTED ERROR: {system_error} ---") # Catches any other unforeseen exceptions


def main():
    # Track information overlay for user viewing
    db = DatabaseManager()
    preferences = db.fetch_user_preferences() # Fetch set of user preferences from SQL database

    if not preferences:
        print("ERROR: Could not load preferences.")
        exit()

    GENRE = preferences.get('active_genre', 'Pop-Punk') # Fetch data for current genre
    GENRE_ID = 1
    SCORE_BLOCKS = int(preferences.get('song_length_blocks', 4))

    print(f"--- Active Genre set to {GENRE} | Number of Song Blocks set to {SCORE_BLOCKS} ---")

    track_rows = db.fetch_track_data(GENRE)
    engine = MusicEngine()
    engine.import_user_preferences(preferences)
    engine.initialize_tracks(track_rows, db)

    engine.generate_song(db, GENRE_ID, track_rows)

    # Main execution flow: Generates a simple 16-step pattern for piano, bass, and drums based on the defined GENRE_MAP; allows user input for filename and includes safety fallback
    save_name = input("Save file as: ")
    if not save_name:
        save_name = "typebeat_default" # Safety fallback if the user only types in symbols

    # Stochastic loop goes here to generate steps of each part of the score
    print("--- Finalizing Score Structure ---")

    save_version(engine.score, db, save_name) # Saves generated score

    db.close()

if __name__ == "__main__":
    main()
import os
import sys

# Imports logic from uploader faculties
from data_inflow.harmonic_map import HarmonicMap
from data_inflow.metadata_sb_upload import MetadataUploader as MacroLibrary
from data_inflow.motifs_upload import MotifUploader as DynamicLibrary

# Verifies the user's input matches a property in the Song Blueprint Enum constraints
from database.connection import SessionLocal
from sqlalchemy import text

# Clears the user's terminal screen for improved visibility ahead of initializing the main menu
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """
    Data upload main user interface:
        Lets the user select between 7 different upload types.
        Seeding programs used for implentation of musical theory data, A.K.A the "Static Library"
        Batch upload programs used for metadata and macro-level musical constraints
        Specialized batch upload for Motif data and Markov chain foundations, A.K.A the "Dynamic Library"
    """

    # Initializes SQLAlchemy classes representing the Typebeat Database
    try:
        test_session = SessionLocal()
        test_session.execute(text("SELECT 1"))
        test_session.close()

        h_map = HarmonicMap()
        m_lib = MacroLibrary()
        d_lib = DynamicLibrary()
    except Exception as e:
        print(f"ERROR: Could not connect to database. ({e})")
        sys.exit(1) # Prevent the menu from loading if the DB is compromised/offline

    # Displays a menu of 8 commands that lets the user select a path depending on the number (0-7) entered
    while True:
        clear_screen()
        print("========================================")
        print("      V7.2 MASS UPLOAD INTERFACE        ")
        print("========================================")
        print(" 1. Seed Static Chords")
        print(" 2. Seed Static Scales")
        print(" 3. Batch Upload Artists")
        print(" 4. Batch Upload Genres")
        print(" 5. Batch Upload Tracks")
        print(" 6. Batch Upload Blueprints")
        print(" 7. Batch Upload Motifs")
        print(" 0. Exit")
        print("========================================")

        choice = input("Select an operation (0-7): ").strip() # Removes whitespace and trailing characters from user input

        # Input 0 - Exits program
        if choice == '0':
            print("Exiting Upload Interface...")
            break

        # Input 1 - Seeds static chord library into 'Chords' and 'Chord Notes' tables
        elif choice == '1':
            print("\n--- SEEDING CHORDS ---")
            result = h_map.seed_basic_chords()

            # Rebuilds the harmonic cache using a temporary session instance to reflect the newly seeded chord data for any upcoming motif uploads that rely on chord mapping
            temp_session = SessionLocal()
            try:
                cache_result = d_lib.build_chord_cache(temp_session)
                if cache_result['status'] == 'success':
                    d_lib.chord_cache = cache_result['data']
                else:
                    print(f"\nChord seeding succeeded, but cache rebuild failed: {cache_result['message']}")
            finally:
                temp_session.close()
            
            print(f"\nRESULT: {result['message']}")
            input("\nChords seeded. Press Enter to Continue...")

        # Input 2 - Seeds static scales library into 'Scales' tables
        elif choice == '2':
            print("\n--- SEEDING SCALES ---")
            result = h_map.seed_scales()
            print(f"\nRESULT: {result['message']}")
            input("\nScales seeded. Press Enter to Continue...")

        # Inputs 3-6 - Allows user to bulk upload a CSV file of artists, genres, tracks, or blueprints into their respective tables
        elif choice in ['3', '4', '5', '6']:
            target_map = {'3': 'artists', '4': 'genres', '5': 'tracks', '6': 'blueprints'}
            target = target_map[choice]

            # Prompts the user to enter the upload path of their CSV file
            path = input(f"Enter path for {target.upper()} CSV: ").strip()
            if os.path.exists(path):
                try:
                    result = m_lib.switchboard(target, path) # If path exists, selects an upload function based on number entered
                    if result['status'] == 'success':
                        print(f"\nSUCCESS: {result['message']}")
                    else:
                        print(f"\nERROR: {result['message']}")
                except Exception as e:
                    print(f"\nERROR: {e}")
            else:
                print(f"File not found: {path}")
            input("\nPress Enter to Return...")

        # Input 7 - Allows user to bulk upload a CSV file of motifs
        elif choice == '7':
            print("\n--- BATCH MOTIF UPLOAD ---")
            path = input(f"Enter Batch Motif CSV path: ").strip()
            if not os.path.exists(path):
                print("File not found.")
                input("\nPress Enter to Return...")
                continue

            session = SessionLocal() # Initialize local session
            try:
                # Initializes Track ID to map the motif to
                while True:
                    try:
                        t_id = int(input("Target Track ID (The motif's parent instrument): ").strip())
                        break
                    except ValueError:
                        print("ERROR: Target Track ID must be a valid integer.")
                
                # Initializes phrase latency modifier
                while True:
                    try:
                        phrase_latency_input = input("Phrase Latency (Optional - default is 0.0): ").strip()
                        phrase_latency = float(phrase_latency_input) if phrase_latency_input else 0.0
                        break
                    except ValueError:
                        print("ERROR: Phrase Latency must be a valid float.")

                # Initializes motif pivot offset modifier
                while True:
                    try:
                        pivot_offset_input = input("Motif Pivot Offset (Optional - default is 0.0): ").strip()
                        motif_pivot_offset = float(pivot_offset_input) if pivot_offset_input else 0.0
                        break
                    except ValueError:
                        print("ERROR: Motif Pivot Offset must be a valid float.")

                transitions_csv_path = input("Transitions Override CSV Path (Optional - Press Enter to Skip): ").strip()
                transitions_csv_path = transitions_csv_path if transitions_csv_path else None

                # Uploads motif with the information provided
                result = d_lib.upload_batch(
                    csv_file_path = path,
                    track_id = t_id,
                    phrase_latency = phrase_latency,
                    motif_pivot_offset = motif_pivot_offset,
                    transitions_csv_path = transitions_csv_path,
                    session = session
                )

                # Commits changes if session was started from this script and not `motifs_upload.py` (Using relayed status message)
                if result['status'] == 'success':
                    session.commit()
                else:
                    session.rollback() # Rolls back changes in case of "error" message

                print(f"\nRESULT: {result['message']}")

            # Checks for any outstanding/miscellaneous errors during upload, rolling back changes if found
            except Exception as e:
                session.rollback()
                print(f"\nERROR: {e}")
            finally:
                session.close()

            input("\nPress Enter to Return...")

if __name__ == "__main__":
    main_menu()
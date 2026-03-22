import os
import sys

# Imports logic from uploader faculties
from scripts.harmonic_map import HarmonicMap
from scripts.metadata_sb_upload import CSVUploader as MacroLibrary
from scripts.motifs_upload import CSVUploader as DynamicLibrary

# Verifies the user's input matches a property in the Song Blueprint Enum constraints
from database.connection import SessionLocal
from database.models import SongBlueprint, SectionClass
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
        Specialized upload for Motif data and Markov chain foundations, A.K.A the "Dynamic Library"
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
        print(" 7. Upload Specialized Motif (Dynamic)")
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

        # Input 7 - Allows user to bulk upload a CSV file of motifs and optionally, foundational transitions for Markov Chain development
        elif choice == '7':
            print("\n--- SPECIALIZED MOTIF UPLOAD ---")
            path = input(f"Enter MOTIF CSV path: ").strip()
            if not os.path.exists(path):
                print("File not found.")
                input("\nPress Enter to Return...")
                continue

            # Prompt user for "Class"" to label their upload motifs under
            name = input("Motif Name (e.g. 'Trap_Lead_A'): ").strip()
            print("Available Blueprint Classes: VERSE, CHORUS, OPENING, BUILD, BRIDGE, etc.")
            m_class = input("Enter Motif Class: ").strip().upper()

            session = SessionLocal() # Initialize local session
            try:
                # Converts the user's input into a Blueprint Enum-readable data type for the database query
                valid_m_class = m_class.replace("-", "_").replace(" ", "_")
                target_block_class = SectionClass[valid_m_class]

                blueprint_exists = session.query(SongBlueprint).filter_by(
                    block_class = target_block_class
                ).first()

                # Checks if a user has uploaded a blueprint block class matching their motif class input
                if not blueprint_exists:
                    print(f"\nERROR: No blueprints for '{m_class}' found in database.")
                    print("Please upload a corresponding Blueprint (Choice 6) before adding motifs.")
                    session.close() # Closes session and exits if validation fails
                    continue

                # Initializes Track ID to map the motif to
                while True:
                    try:
                        t_id = int(input("Target Track ID (The motif's parent instrument): ").strip())
                        break
                    except ValueError:
                        print("ERROR: Target Track ID must be a valid integer.")

                # Optional: Initializes transition (Previous motif ID) to set up Markov chains
                while True:
                    from_id_input = input("From Motif ID (Optional - Enter to skip): ").strip()
                    if not from_id_input:
                        f_id = None
                        break
                    try:
                        f_id = int(from_id_input)
                        break
                    except ValueError:
                        print("ERROR: Motif ID must be a valid integrer or left blank.")

                # Uploads motif with the information provided
                result = d_lib.upload_motif(
                    csv_file_path = path,
                    motif_name = name,
                    m_class_str = m_class,
                    track_id = t_id,
                    from_motif_id = f_id,
                    session = session
                )

                # Commits changes if session was started from this script and not `motifs_upload.py` (Using relayed status message)
                if result['status'] == 'success':
                    session.commit()
                else:
                    session.rollback() # Rolls back changes in case of "error" message

                print(f"\nRESULT: {result['message']}")

            # Checks if the user's input exists in the Blueprint Enum constraints
            except KeyError:
                print(f"\nERROR: '{m_class}' is not a valid Blueprint or Motif class.")
            # Checks for any outstanding/miscellaneous errors during upload, rolling back changes if found
            except Exception as e:
                session.rollback()
                print(f"\nERROR: {e}")
            finally:
                session.close()  

if __name__ == "__main__":
    main_menu()
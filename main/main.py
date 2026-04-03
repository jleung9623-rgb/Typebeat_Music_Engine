import os
from database.connection import SessionLocal
from database.models import Artist, Genre, Track, Composition
from engine.data_initialization import build_metadata_profile, build_track_profile, build_blueprint_profile
from engine.markov_engine import run_generator
from engine.harmonic_analyzer import transpose_motif
from engine.midi_builder import build_midi_file
from engine.aliases import SCALE_ALIASES, ROOT_ALIASES


def validate_track_request(session, track_name):
    """Validates that a track request from the user input matches an existing track in the database to prevent errors during generation."""
    exists = session.query(Track).filter(Track.track_name == track_name).first()
    return bool(exists)


def main(song_length=80):
    """Main execution function for the TypeBeat Orchestrator. Handles user input, data fetching, and final MIDI output generation."""
    session = SessionLocal()

    print("\n--- SYSTEM INITIALIZATION ---")

    # Selects Artist for composition using user input; Validates existence in database and returns Artist object
    print("\n--- ARTIST SELECTION ---")
    artist = input("\nEnter Artist Name: ").strip()
    artist_exists = session.query(Artist).filter(Artist.artist_name == artist).first()
    
    if not artist_exists:
        print(f"ERROR: Artist '{artist}' not found.")
        session.close()
        return
        
    # Selects Genre for composition using user input; Validates existence in database and returns Genre object
    print("\n--- GENRE SELECTION ---")
    genre = input("\nEnter Genre: ").strip()
    genre_exists = session.query(Genre).filter(Genre.genre_name == genre).first()
    if not genre_exists:
        print(f"ERROR: Genre '{genre}' not found.")
        session.close()
        return

    # Selects Track(s) for composition using user input; Validates existence in database and returns Track objects
    print("\n--- TRACK SELECTION ---")
    print("\nAvailable Track Types: PERCUSSION, BASS, MELODIC_LEAD, etc.")
    track_requests = []

    while True:
        track_input = input("\nEnter Track Names: ").strip().upper()

        # Breaks the loop and moves to the next step of the process if user types 'DONE', checking if the user has selected a minimum number of tracks
        if track_input == 'DONE':
            if not track_requests:
                print("ERROR: You must select at least one track.")
                continue
            break
        
        # If track(s) have been validated, prompts user to enter scale information before adding the track to the list of selected tracks for the composition
        if validate_track_request(session, track_input):
            # Initializes scale information, using a dictionary of aliases to allow for flexible user input regarding scale name and root notes
            scale_input = input(f"Enter Scale for {track_input} or Press Enter for default/random scale: ").strip().lower()
            root_input = input(f"Enter Root Note for {track_input} (e.g., 'C#') or Press Enter for default root: ").strip().lower()

            track_payload: dict[str, str | int] = {'track_name': track_input}

            # Uses the alias dictionaries to map user input to the correct scale and root note information for the track; If no input is provided, defaults are used based on the track's assigned scale in the database or a random scale if no default is designated
            if scale_input:
                final_scale = SCALE_ALIASES.get(scale_input, scale_input.title())
                track_payload['scale_name'] = final_scale
                print(f"Final scale '{final_scale}' routed to track '{track_input}'.")

            if root_input:
                final_root = ROOT_ALIASES.get(root_input)
                if final_root:
                    track_payload['root_override'] = final_root
                else:
                    print(f"ERROR: Root note '{root_input}' not recognized. Reverting to default value for this track.")

            track_requests.append(track_payload)
            print(f"Track '{track_input}' has been validated and added.")
        else:
            print(f"Track '{track_input}' not found in database. Please enter a valid track name or type 'DONE' to finish.")

    # Designates generated MIDI file name and output directory based on user input; Validates existence of output directory
    print("\n--- EXPORT CONFIGURATION ---")
    file_name = input("Enter Output File Name: ").strip()
    file_path = input("Enter File Path: ").strip()
    if not os.path.exists(file_path):
        print("ERROR: File path not found.")
        session.close()
        return

    # Final MIDI output generation - Includes error handling and validation to ensure each step of the process is successful; rolls back any database changes if an error occurs during generation
    try:
        print("\nSYSTEM: Constructing Final MIDI Payload...")
        
        # Constructs Final Payload for Markov Engine using the worker functions to fetch the necessary information
        metadata = build_metadata_profile(
            session=session,
            artist_requests=artist,
            genre_requests=genre,
            song_length=song_length
        )

        tracks = build_track_profile(
            session=session,
            track_requests=track_requests
        )

        blueprints = build_blueprint_profile(
            session=session,
            genre_name=genre
        )

        # Packages Final Payload variables into a single dictionary to be sent to the Markov Engine
        final_payload = {
            'metadata': metadata,
            'tracks': tracks,
            'blueprints': blueprints
        }

        # Executes Markov Engine to generate composition timeline
        print("\nSYSTEM: Running Markov Engine...")
        master_timeline = run_generator(session, final_payload)

        # Validates output to ensure timeline was generated successfully before proceeding to post-production
        if not master_timeline:
            raise ValueError("Timeline generation failed. Markov Engine returned empty values.")

        # Processes & Renders Composition (MIDI File Output)
        print("\nApplying Post Production...")
        final_midi_data = []

        # Iterates through each track's generated timeline to apply the necessary transposition based on the track's scale and key information
        for active_track in final_payload['tracks']:
            current_track_id = active_track.get('track_id')

            c_track_timeline = master_timeline.get(current_track_id)

            if not c_track_timeline:
                print(f"ERROR: No timeline generated for Track ID {current_track_id}. Skipping post-production for this track.")
                continue

            print(f"Transposing composition timeline for: {active_track.get('track_name', 'Unknown')}")
            
            track_midi_data = transpose_motif(session, c_track_timeline, active_track)
            final_midi_data.extend(track_midi_data)

        # Validates that MIDI data was generated successfully before proceeding to file output
        if not final_midi_data:
            raise ValueError("ERROR: No MIDI events detected in post-production. Cannot render MIDI file.")

        print("\nSaving MIDI File...")

        # Builds MIDI file from the final MIDI data output and saves it to the user-specified file path with the user-designated file name
        final_file_path, final_name = build_midi_file(
            global_midi_data = final_midi_data, 
            file_name=file_name,
            metadata=metadata,
            output_dir=file_path
        )

        # Uploads the generated composition's file information to the database under the Artist's profile and commits the changes to the live schema
        print("SYSTEM: Committing Composition to Live Schema...")
        final_composition = Composition(
            artist_id = artist_exists.id,
            file_path = final_file_path,
            file_name = final_name
        )

        session.add(final_composition)
        session.commit()

    # Rolls back the server session in case of any exceptions during the generation process to prevent partial or corrupted data from being committed to the database
    except Exception as e:
        print(f"ERROR: An error occurred during generation: {e}")
        session.rollback()

    finally:
        session.close()

if __name__ == "__main__":
    main()
import pandas as pd
from sqlalchemy import insert
from sqlalchemy.orm import joinedload
from database.connection import SessionLocal
from database.models import Motif, MotifNote, track_motif_map, SectionClass, Transition, MotifStat, Chord, ChordNote

class CSVUploader:
    def __init__(self):
        self.chord_cache = self.build_chord_cache()

    def build_chord_cache(self):
        """
        Loads the entire Chord library into memory.
        Maps (root_pitch_class, interval_tuple) -> chord_id
        """

        # Initializes local session and empty container for sole purpose of organizing chord data
        session = SessionLocal()
        cache = {}

        # Joins Chord Notes table with 'Chords' using the 'is_verified' column before executing a filtered query to grab all eligible rows of chords
        try:
            chords = session.query(Chord).options(joinedload(Chord.chord_notes)).filter_by(is_verified=True).all()
            
            # Checks if applicable chords have existing note data
            for chord in chords:
                if not chord.chord_notes:
                    continue

                # Consolidates all chord note pitch values into a sorted list
                pitches = sorted([cn.pitch_value for cn in chord.chord_notes])
                
                # Designates the first list entry as the root pitch and converts it to an absolute value on the chromatic scale representing the actual note
                root_pitch = pitches[0]
                root_pitch_class = root_pitch % 12

                # Calculates the interval value of each chord note and casts the final list into a tuple
                intervals = tuple(p - root_pitch for p in pitches)

                # Maps the corresponding information within the tuple key into the Chord ID
                cache[(root_pitch_class, intervals)] = chord.id

            return cache
        
        # Checks if harmonic cache was properly initialized; Uses a raise call to force the program to crash with a specific error message
        except Exception as e:
            print(f"ERROR: Failed to initialize harmonic cache. Cannot proceed: {e}")
            raise

        finally:
            session.close() # Closes instance of session once cache has been built
    
    def upload_motif(self, csv_file_path, motif_name, m_class_str, track_id, phrase_latency=0.0, pivot_offset=0.0, from_motif_id=None, transition_weight=1.0, session=None):
        """
        Specialized Ingestor:
        1. Creates the Motif (Name/Metadata)
        2. Links to Track (Junction)
        3. Generates Motif Taxonomy Token
        4. Bulk Inserts Notes (Performance)
        5. OPTIONAL: Creates a Transition from a previous Motif
        """

        # Checks if external session is already active, creates a local session if not
        external_session = session is not None
        if not external_session:
            session = SessionLocal()

        try:
            # Initializes DataFrame/DF Columns
            df = pd.read_csv(csv_file_path)
            df.columns = df.columns.str.strip()

            # Validates required list of columns for upload
            required_columns = ['pitch_value', 'beat_position', 'duration']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"ERROR: CSV format rejected. Missing required columns: {missing_columns}")
            
            # Validates all required columns contain data
            if df[required_columns].isnull().values.any():
                raise ValueError(f"ERROR: CSV format rejected. Empty cells detected in required columns.")

            # Converts the user's input into a Blueprint Enum-readable data type for the database query
            try:
                valid_class_str = m_class_str.upper().replace("-", "_").replace(" ", "_")
                m_class_enum = SectionClass[valid_class_str]
            except KeyError:
                raise ValueError(f"Invalid MotifClass: {m_class_str}. Check your Enum definitions.")

            # Initializes new motif object
            new_motif = Motif(
                motif_name = motif_name,
                motif_class = m_class_enum,
                sequence_data = "PENDING", # Will update once ID is collected
                phrase_latency = float(phrase_latency),
                motif_pivot_offset = float(pivot_offset)
            )
            session.add(new_motif)
            session.flush() # Syncs with DB to collect new_motif.id

            # Initializes new motif stats object
            new_stats = MotifStat(
                motif_id = new_motif.id,
                occurrence_count = 0
            )
            session.add(new_stats)

            # Links motif to track
            try:
                with session.begin_nested():
                    junction_link = track_motif_map.insert().values(
                        track_id = track_id,
                        motif_id = new_motif.id,
                        selection_weight = 1.0,
                        octave_shift = 0
                    )
                    session.execute(junction_link)
            except Exception as e:
                raise ValueError(f"ERROR: Failed to link Motif to Track {track_id}. Ensure Track ID exists. Error: {e}")

            # Generates metadata taxonomy token; uses a truncated Class prefix (First 3 letters) for optimized indexing
            new_motif.sequence_data = f"M{new_motif.id}_{m_class_enum.name[:3]}"

            # Groups notes by beat position to then be appended as chords
            notes_list = []
            grouped_notes = df.groupby('beat_position')

            # Sorts each group of chord note pitch values into a list of integers
            for _, group in grouped_notes:
                pitches = sorted(group['pitch_value'].astype(int).tolist())

                c_id = None

                # Grabs the first entry of the chord note list, finding its root note and interval values before converting them into a tuple key
                if len(pitches) > 1:
                    root_pitch = pitches[0]
                    root_pitch_class = root_pitch % 12
                    intervals = tuple([p - root_pitch for p in pitches])

                    c_id = self.chord_cache.get((root_pitch_class, intervals))

                # Initializes each motif note object before appending them to the list of notes
                for _, row in group.iterrows():
                    note = MotifNote(
                        motif_id = new_motif.id,
                        chord_id = c_id,
                        pitch_value = int(row['pitch_value']),
                        duration = float(row['duration']),
                        beat_position = float(row['beat_position']),
                        micro_offset = float(row.get('micro_offset', 0.0))
                    )
                    notes_list.append(note)
                
            session.add_all(notes_list) # Adds the list of notes to the database

            # Establishes a link from a preceding motif to create a Markov chain structure
            transition_status = "None"
            if from_motif_id is not None:
                new_transition = Transition(
                    from_motif_id = from_motif_id,
                    to_motif_id = new_motif.id,
                    transition_weight = transition_weight
                )
                session.add(new_transition)
                transition_status = f"Linked from Motif ID {from_motif_id}"

            # Only commits changes here in local instances
            if not external_session:
                session.commit()

            # Success message will be used in `upload_interface.py`
            return {
                "status": "success",
                "message": f"Uploaded '{motif_name}' (ID: {new_motif.id}) with {len(notes_list)} notes.",
                "motif_id": new_motif.id,
                "notes": len(notes_list),
                "transition": transition_status
            }

        # Catches any outstanding/miscellaneous errors
        except Exception as e:
            if not external_session:
                session.rollback()

            # Checks whether a Chord ID that doesn't exist in the database is currently being used
            error_msg = str(e)
            if "foreign key constraint fails" in error_msg.lower() and "chords" in error_msg.lower():
                return {"status": "error", "message": "ERROR: CSV contains a chord_id that does not exist in the database."}

            return {"status": "error", "message": str(e)}
        
        finally:
            if not external_session:
                session.close()

if __name__ == "__main__":
    engine = CSVUploader()
import pandas as pd
from sqlalchemy import insert
from database.connection import SessionLocal
from database.models import Motif, MotifNote, track_motif_map, SectionClass, Transition, MotifStat

class CSVUploader:
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

            # Prepares notes in bulk
            notes_list = []
            for _, row in df.iterrows():
                c_id = int(row['chord_id']) if 'chord_id' in df.columns and pd.notna(row['chord_id']) else None
                
                # Initializes Motif Note object
                note = MotifNote(
                    motif_id = new_motif.id,
                    chord_id = c_id,
                    pitch_value = int(row['pitch_value']),
                    duration = float(row['duration']),
                    beat_position = float(row['beat_position']),
                    micro_offset = float(row.get('micro_offset', 0.0))
                )
                notes_list.append(note)
            
            session.add_all(notes_list)

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
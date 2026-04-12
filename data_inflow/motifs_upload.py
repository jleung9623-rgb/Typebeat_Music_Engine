import pandas as pd
from sqlalchemy.orm import joinedload
from database.connection import SessionLocal
from database.models import Motif, MotifNote, track_motif_map, SectionClass, Transition, MotifStat, Chord, ChordNote
from data_inflow.transitions_upload import TransitionBuilder

class MotifUploader:
    def __init__(self):
        self.chord_cache = None

    def build_chord_cache(self, session):
        """
        Loads the entire Chord library into memory.
        Maps (root_pitch_class, interval_tuple) -> chord_id
        """

        cache = {}

        # Joins Chord Notes table with 'Chords' using the 'is_verified' column before executing a filtered query to grab all eligible rows of chords
        try:
            chords = session.query(Chord).options(joinedload(Chord.chord_notes)).filter_by(is_verified=True).all()
            
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

            return {"status": "success", "data": cache}
        
        # Checks if harmonic cache was properly initialized; Uses a raise call to force the program to crash with a specific error message
        except Exception as e:
            return {"status": "error", "message": f"Failed to initialize chord cache: {e}"}


    def upload_batch(self, csv_file_path, track_id, phrase_latency=0.0, motif_pivot_offset=0.0, transitions_csv_path=None, session=None):
        """
        Unified Batch Motif Uploader:
        Handles motif generation, junction mapping, and bulk note inserts.
        1. Verifies contents of CSV file is eligible for upload
        2. Adds required Motif upload data to a queue
        3. Creates a junction table link, adding relational data
        4. Adds required Motif Note and Chord-level data to a queue
        5. Commits final upload to the database
        """

        # Initializes local session if the program is not being accessed from an external process
        external_session = session is not None
        if not external_session:
            session = SessionLocal()
        
        if not self.chord_cache:
            cache_result = self.build_chord_cache(session)
            if cache_result["status"] == "error":
                if not external_session: session.close()
                return cache_result
            self.chord_cache = cache_result["data"]

        # Sets up a batch upload for motifs through a CSV file that is routed into the SQL database
        try:
            # Initializes pandas dataframe property, converting all columns into a readable format
            df = pd.read_csv(csv_file_path)
            df.columns = df.columns.str.strip()

            # Designates the list of required columns for upload
            required_columns = ['motif_name', 'motif_class', 'pitch_value', 'beat_position', 'duration']
            missing_columns = [col for col in required_columns if col not in df.columns]

            # Checks if the user is missing any required columns in their file, or has empty cell data in their required columns
            if missing_columns:
                raise ValueError(f"ERROR: CSV format rejected. Missing required columns: {missing_columns}")
            
            if df[required_columns].isnull().values.any():
                raise ValueError(f"ERROR: CSV format rejected. Empty cells detected in required columns.")
            
            # Groups motifs by their name and class to establish the required 1-to-Many database relationship between motifs and their notes
            grouped_motifs = df.groupby(['motif_name', 'motif_class'])

            motifs_created = 0
            motif_notes_created = 0

            # Iterates through each relationship grouping using the established key, uploading each motif and their notes to the database
            for (m_name, m_class_str), motif_group in grouped_motifs:
                # Verifies if the motif's class is valid based on its corresponding Enum label
                try:
                    valid_class_str = str(m_class_str).upper().replace("-", "_").replace(" ", "_")
                    m_class_enum = SectionClass[valid_class_str]
                except KeyError:
                    raise ValueError(f"Invalid MotifClass: {m_class_str} for motif {m_name}.")
                
                # Designates the required Motif information before adding it to the upload queue and flushing all cached data
                new_motif = Motif(
                    motif_name = str(m_name),
                    motif_class = m_class_enum,
                    sequence_data = 'PENDING',
                    phrase_latency = float(phrase_latency),
                    motif_pivot_offset = float(motif_pivot_offset)
                )
                session.add(new_motif)
                session.flush()

                # Designates the required Motif metadata information before adding it to the upload queue
                new_motif_stats = MotifStat(
                    motif_id = new_motif.id,
                    occurrence_count = 0
                )
                session.add(new_motif_stats)

                # Uses a savepoint to establish link to junction table, skipping over assignment of current motif and continuing if mapping it fails
                try:
                    with session.begin_nested():
                        junction_link = track_motif_map.insert().values(
                            track_id = track_id,
                            motif_id = new_motif.id,
                            selection_weight = 1.0, # Will eventually update to be a dynamic value
                            octave_shift = 0
                        )
                        session.execute(junction_link)
                except Exception as e:
                    raise ValueError(f"Junction mapping collision for Motif {new_motif.id} to Track {track_id}: {e}")
                
                # Initializes note sequence data key using motif ID and indexable Enum label
                new_motif.sequence_data = f"M{new_motif.id}_{m_class_enum.name[:3]}"

                notes_list = []
                grouped_notes = motif_group.groupby('beat_position')

                # Iterates through all motif notes and chords (grouped notes), mapping their respective musical information to database properties
                for _, beat_group in grouped_notes:
                    pitch_values = sorted(beat_group['pitch_value'].astype(int).tolist())
                    c_id = None

                    # Assigns a Chord ID, root pitch value, and semitone intervals for note groups with more than 1 pitch value detected
                    if len(pitch_values) > 1:
                        root_pitch = pitch_values[0]
                        root_pitch_class = root_pitch % 12
                        intervals = tuple([p - root_pitch for p in pitch_values])
                        c_id = self.chord_cache.get((root_pitch_class, intervals)) # type: ignore

                    # Iterates through dataframe rows for motif notes, mapping their required information to the MotifNote class before adding it to the total list of notes
                    for _, row in beat_group.iterrows():
                        note = MotifNote(
                            motif_id = new_motif.id,
                            chord_id = c_id,
                            pitch_value = int(row['pitch_value']),
                            duration = float(row['duration']),
                            beat_position = float(row['beat_position']),
                            micro_offset = float(row.get('micro_offset', 0.0))
                        )
                        notes_list.append(note)

                # Adds the final note list to the upload queue, logging the number of motifs and their respective notes created
                session.add_all(notes_list)
                motifs_created += 1
                motif_notes_created += len(notes_list)

            if not external_session:
                session.commit()
            
            # Routes user through the transition mapping process, adding proper to/from motif transitions for use in the Markov Engine
            try:
                transition_mapper = TransitionBuilder()
                result = transition_mapper.map_transitions(
                    track_id = track_id,
                    csv_file_path = transitions_csv_path
                )
                if result['status'] == 'error':
                    print(f"ERROR: Motifs uploaded, but transition mapping failed: {result['message']}")
                
            except Exception as e:
                print(f"ERROR: Motifs uploaded but transition mapper has crashed: {str(e)}")
            
            return {
                "status": "success",
                "message": f"Batch complete. Uploaded {motifs_created} motifs and {motif_notes_created} notes."
            }
        
        # Checks if any outstanding issues occurred during the batch upload process before closing the session as a failsafe
        except Exception as e:
            if not external_session:
                session.rollback()
            return {"status": "error", "message": str(e)}
        
        finally:
            if not external_session:
                session.close()

if __name__ == "__main__":
    engine = MotifUploader()
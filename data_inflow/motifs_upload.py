import uuid
import torch
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from database.connection import SessionLocal
from database.models import Motif, MotifNote, track_motif_map, SectionClass, Transition, MotifStat, Chord, ChordNote
from data_inflow.transitions_upload import TransitionBuilder
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

class MotifUploader:
    def __init__(self):
        self.chord_cache = None

        self.qdrant = QdrantClient(path="./qdrant_db")
        self.collection_name = "typebeat_motifs"
        
        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name = self.collection_name,
                vectors_config = VectorParams(size=256, distance=Distance.COSINE)
            )
        
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        print(f"--- Booting PyTorch Inference Engine on {self.device.type.upper()} ---")

        try:
            self.model = torch.jit.load("ml/typebeat_embedding_model.pt").to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"ERROR: Neural model 'ml/typebeat_embedding_model.pt' not found. Inference will fail: {e}")
            self.model = None

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
        
    def embed_neurosymbolic_coordinate(self, motif_group_df):
        """
        Translates the physical motif data into a PyTorch tensor, executes the forward pass,
        and detaches the resulting 256-dimensional spatial array for Qdrant ingestion.
        """

        if self.model is None:
            raise RuntimeError("ERROR: Neural model not loaded in memory. Aborting extraction process.")
        
        # Pulls the continuous float coordinates from the Pandas dataframe
        raw_features = motif_group_df[['pitch_value', 'duration', 'beat_position', 'micro_offset']].values

        # Casts the "trait" of features to a float32 (standard neural network precision) format and adds the Batch Dimension (1, Seq_Len, Features)
        input_tensor = torch.tensor(raw_features, dtype=torch.float32).unsqueeze(0).to(self.device)

        # Disables gradient calculation to prevent memory leaks during mass ingestion
        with torch.no_grad():
            output_embedding = self.model(input_tensor)

        # Strips the tensor from the GPU/CPU computational graph and casts to a standard Python list for Qdrant
        return output_embedding.squeeze().cpu().tolist()
    
    def upload_batch(self, csv_file_path, track_id, phrase_latency=0.0, transitions_csv_path=None, session=None):
        """
        Unified Batch Motif Uplaoder:
        Executes atomic dual-writes to Qdrant and MySQL using a Compensating Transaction pattern.
        """

        # Checks if the script is being accessed from an external program in the workflow, creating a local session if not
        external_session = session is not None
        if not external_session:
            session = SessionLocal()

        # Validates the chord cache has been built, creating it if it doesn't exist
        if not self.chord_cache:
            cache_result = self.build_chord_cache(session)
            if cache_result["status"] == "error":
                if not external_session: session.close()
                return cache_result
            self.chord_cache = cache_result["data"]

        # Main batch upload execution loop
        try:
            # Initializes a Pandas DataFrame property using the designated CSV file
            df = pd.read_csv(csv_file_path)
            df.columns = df.columns.str.strip()

            # Initializes the list of required columns, checking if the CSV has any missing columns or empty cells within the required columns
            required_columns = {'motif_name', 'motif_class', 'motif_pivot_offset', 'rest_duration', 'rest_suffix', 'phrase_latency', 'pitch_value', 'beat_position', 'duration'}
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"ERROR: CSV format rejected. Missing required columns: {missing_columns}")
            
            if df[required_columns].isnull().values.any():
                raise ValueError(f"ERROR: CSV format rejected. Empty cells detected in required columns.")
            
            # Creates a key used to identify motif groups (Based on their names and classes)
            grouped_motifs = df.groupby(['motif_name', 'motif_class'])

            motifs_created = 0
            motif_notes_created = 0

            # Iterates through each motif group, embedding a vector coordinate value (Neural Engine) and musical profile (SQL Database) per motif
            for (m_name, m_class_str), motif_group in grouped_motifs:
                try:
                    valid_class_str = str(m_class_str).upper().replace("-", "_").replace(" ", "_")
                    m_class_enum = SectionClass[valid_class_str]
                except KeyError:
                    raise ValueError(f"Invalid MotifClass: {m_class_str} for motif {m_name}.")
                
                # Executes neural extraction by embedding a motif into a vector coordinate value
                raw_embed = self.embed_neurosymbolic_coordinate(motif_group)
                shared_vector_id = str(uuid.uuid4())

                # Creates a key-value pairing (A complete vector coordinate) for the neural engine using the embedded vector and the payload "trait"
                try:
                    self.qdrant.upsert(
                        collection_name = self.collection_name,
                        points = [
                            PointStruct(
                                id = shared_vector_id,
                                vector = raw_embed,
                                payload = {
                                "motif_class": valid_class_str,
                                "track_id": track_id
                                }
                            )
                        ]
                    )
                except Exception as e:
                    print(f"CRITICAL: Vector write failed for {m_name}. MySQL transaction bypassed. {e}")
                    raise e # Aborts batch to maintain integrity
                
                # Writes the motif profile data to the internal system (Typebeat SQL Database)
                try:
                    first_row = motif_group.iloc[0]
                    rest_suffix_tag = str(first_row.get('rest_suffix', 'NONE'))
                    phrase_latency = float(first_row.get('phrase_latency', 0.0))
                    
                    new_motif = Motif(
                        motif_name = str(m_name),
                        motif_class = m_class_enum,
                        sequence_data = 'PENDING',
                        phrase_latency = phrase_latency,
                        motif_pivot_offset = float(first_row.get('motif_pivot_offset', 0.0)),
                        rest_duration = float(first_row.get('rest_duration', 0.0)),
                        rest_suffix = rest_suffix_tag,
                        vector_id = shared_vector_id
                    )
                    session.add(new_motif)
                    session.flush()

                    new_motif_stats = MotifStat(
                        motif_id = new_motif.id,
                        occurrence_count = 0
                    )
                    session.add(new_motif_stats)

                    # Establishes a junction link with the 'track_motif_map' table
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
                        raise ValueError(f"Junction mapping collision for Motif {new_motif.id} to Track {track_id}: {e}")
                    
                    # Generates motif sequence data (For high-order Markov logic)
                    new_motif.sequence_data = f"M{new_motif.id}_{m_class_enum.name[:3]}"

                    # Groups notes by temporal location ('beat_position') to identify note stacks
                    notes_list = []
                    grouped_notes = motif_group.groupby('beat_position')

                    # Iterates through each note stack, assigning a 'chord_id' if the corresponding chord exists in the static library
                    for _, beat_group in grouped_notes:
                        pitch_values = sorted(beat_group['pitch_value'].astype(int).tolist())
                        c_id = None

                        if len(pitch_values) > 1:
                            root_pitch = pitch_values[0]
                            root_pitch_class = root_pitch % 12
                            intervals = tuple([p - root_pitch for p in pitch_values])
                            c_id = self.chord_cache.get((root_pitch_class, intervals)) # type: ignore

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

                    session.add_all(notes_list)

                    if not external_session:
                        session.commit()

                    # Logs number of motifs and motif notes created
                    motifs_created += 1
                    motif_notes_created += len(notes_list)

                # Validates if all musical profiles were successfully uploaded to the database, rolling back all changes if an error occurs here
                except SQLAlchemyError as e:
                    if not external_session:
                        session.rollback()
                    print(f"ERROR: MySQL insertion falied for {m_name}. Relational state has been rolled back.")
                
                    # Additionally, removes the orphaned vector from the Qdrant library, simulating a rollback process similar to the SQL protocol
                    try:
                        self.qdrant.delete(
                            collection_name = self.collection_name,
                            points_selector = [shared_vector_id]
                        )
                        print(f"COMPENSATION SUCCESS: Orphaned vector {shared_vector_id} deleted from Qdrant.")

                    except Exception as q_err:
                        print(f"COMPENSATION FAILURE: Orphaned vector {shared_vector_id} could not be deleted from Qdrant: {q_err}")
                        
                    raise e # Raises original error to maintain integrity of batch process
                
            # Maps transitions for the newly uploaded motifs using the provided transitions CSV file
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
            
        except Exception as e:
            if not external_session:
                session.rollback()
            return {"status": "error", "message": str(e)}
        
        finally:
            if not external_session:
                session.close()


if __name__ == "__main__":
    engine = MotifUploader()
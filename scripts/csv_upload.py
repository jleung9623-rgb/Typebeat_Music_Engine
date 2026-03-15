import pandas as pd
from sqlalchemy import insert
from database.connection import SessionLocal
from database.models import Motif, MotifNote, track_motif_map, MotifClass, Transition

class CSVUploader:
    def __init__(self):
        self.session = SessionLocal()

    def upload_motif(self, csv_file_path, motif_name, m_class_str, track_id, from_motif_id=None, transition_weight=1.0):
        """
        Specialized Ingestor:
        1. Creates the Motif (Metadata)
        2. Links to Track (Junction)
        3. Generates Motif Taxonomy Token
        4. Bulk Inserts Notes (Performance)
        5. OPTIONAL: Creates a Transition from a previous Motif
        """
        try:
            df = pd.read_csv(csv_file_path)
            df.columns = df.columns.str.strip()

            try:
                m_class_enum = MotifClass[m_class_str.upper()]
            except KeyError:
                raise ValueError(f"Invalid MotifClass: {m_class_str}. Check your Enum definitions.")
            
            new_motif = Motif(
                motif_name = motif_name,
                motif_class = m_class_enum,
                sequence_data = "PENDING" # Will update once ID is collected
            )
            self.session.add(new_motif)
            self.session.flush() # Syncs with DB to get new_motif.id

            junction_link = track_motif_map.insert().values(
                track_id = track_id,
                motif_id = new_motif.id,
                selection_weight = 1.0,
                octave_shift = 0
            )
            self.session.execute(junction_link)

            # Generate taxonomy token
            new_motif.sequence_data = f"M{new_motif.id}_T{track_id}_{m_class_enum.name[:3]}"

            notes_list = []
            for _, row in df.iterrows():
                c_id = int(row['chord_id']) if 'chord_id' in df.columns and pd.notna(row['chord_id']) else None

                note = MotifNote(
                    motif_id = new_motif.id,
                    chord_id = c_id,
                    pitch_value = int(row['pitch_value']),
                    duration = float(row['duration']),
                    beat_position = float(row['beat_position']),
                    micro_offset = float(row.get('micro_offset', 0.0))
                )
                notes_list.append(note)
            
            self.session.add_all(notes_list)

            transition_status = "None"
            if from_motif_id is not None:
                new_transition = Transition(
                    from_motif_id = from_motif_id,
                    to_motif_id = new_motif.id,
                    transition_weight = transition_weight
                )
                self.session.add(new_transition)
                transition_status = f"Linked from Motif ID {from_motif_id}"

            self.session.commit()
            return {
                "status": "success",
                "motif_id": new_motif.id,
                "notes": len(notes_list),
                "transition": transition_status
            }

        except Exception as e:
            self.session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            self.session.close()

if __name__ == "__main__":
    engine = CSVUploader()
import os
import pandas as pd
from database.connection import SessionLocal
from database.models import Motif, Transition, track_motif_map, genre_track_map, genre_blueprint_map, SongBlueprint

class TransitionBuilder:
    """Builds motif transitions from a parent track."""

    def __init__(self):
        pass

    def map_transitions(self, track_id, csv_file_path=None):
        """
        Maps transition states (Current/Next Paths) for motifs through the following steps:
            1. Maps all eligible transition states based on an existing track's motifs, the motifs' special 'motif_tags', and their blueprint block positions
            2. If a CSV file path was entered (From `upload_interface.py`), grants the ability to map custom transition weightings for motifs based on file data
        """
        session = SessionLocal()

        try:
            # Fetches all of a track's Motif IDs as a reference to pull transition data from
            track_motifs_query = session.query(Motif.id).join(track_motif_map).filter(
                track_motif_map.c.track_id == track_id
            )

            # Fetches all available motifs with transitional 'from_motif_id' values within the track
            session.query(Transition).filter(
                Transition.from_motif_id.in_(track_motifs_query)
            ).delete(synchronize_session=False)
            session.flush()

            # Fetches the parent genre of the designated track for upcoming blueprints query
            track_genres_query = session.query(genre_track_map.c.genre_id).filter(
                genre_track_map.c.track_id == track_id
            )

            # Fetches all of the blueprint blocks from the track's parent genre to be used for sequential mapping logic
            blueprints = session.query(SongBlueprint).join(genre_blueprint_map).filter(
                genre_blueprint_map.c.genre_id.in_(track_genres_query)
            ).order_by(SongBlueprint.block_position).all()

            # Creates the first skeleton grouping for valid class transitions while ensuring motifs are mapped according to song structure
            # Uses a key for current and next class for blueprint block transitions, mapping each corresponding pair of current/next values to a 'validated' list
            valid_class_transitions = set()
            for i in range(len(blueprints)):
                current_class = blueprints[i].block_class
                valid_class_transitions.add((current_class, current_class))

                if i + 1 < len(blueprints):
                    next_class = blueprints[i+1].block_class
                    valid_class_transitions.add((current_class, next_class))

            # Initializes second grouping of motifs with a key based on each motif's SectionClass label (For Blueprint order/consistency) and their additional 'motif_tag' label (For building coherent musical patterns)
            motifs = session.query(Motif).join(track_motif_map).filter(
                track_motif_map.c.track_id == track_id
            ).all()

            motif_dict = {}

            for m in motifs:
                key = (m.motif_class, m.motif_tag)
                if key not in motif_dict:
                    motif_dict[key] = []
                motif_dict[key].append(m.id)

            # Initializes the set of first-level transition states (Keys representing pairs of Motif IDs and Tags) for all eligible motifs filtered through the previous groupings
            baseline_transitions = []

            for (from_class, to_class) in valid_class_transitions:
                for tag in set(m.motif_tag for m in motifs):
                    from_ids = motif_dict.get((from_class, tag), [])
                    to_ids = motif_dict.get((to_class, tag), [])

                    for f_id in from_ids:
                        for t_id in to_ids:
                            baseline_transitions.append(Transition(
                                from_motif_id = f_id,
                                to_motif_id = t_id,
                                transition_weight = 1.0
                            ))

            session.add_all(baseline_transitions)
            session.flush()

            # If an existing CSV file exists, executes a CSV upload override for transition weighting values instead of manually seeding them
            if csv_file_path and os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path)
                df.columns = df.columns.str.strip()

                # Designates the list of required columns for upload and checks if any of the columns are missing or if cells have empty data
                required_columns = ['from_motif_name', 'to_motif_name', 'transition_weight']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"CSV format rejected. Missing required columns: {missing_columns}")
                
                if df[required_columns].isnull().values.any():
                    raise ValueError(f"ERROR: CSV format rejected. Empty cells detected in required columns.")
                
                # Fetches the Motif table's row data for each to/from motif, mapping the corresponding transitional data from the CSV if they are found
                for _, row in df.iterrows():
                    # Fetches the motif names from the database matching the required column data in the CSV file
                    from_motif = session.query(Motif).join(track_motif_map).filter(
                        track_motif_map.c.track_id == track_id,
                        Motif.motif_name == str(row['from_motif_name'])
                    ).first()
                    to_motif = session.query(Motif).join(track_motif_map).filter(
                        track_motif_map.c.track_id == track_id,
                        Motif.motif_name == str(row['to_motif_name'])
                    ).first()

                    # Skips over current row if either transition motif is not found
                    if not from_motif or not to_motif:
                        continue

                    # Checks if an existing transition is present for the row, overriding the transition weight if it does exist and mapping a new transition weight if it doesn't
                    existing_transition = session.query(Transition).filter_by(
                        from_motif_id = from_motif.id,
                        to_motif_id = to_motif.id
                    ).first()

                    if existing_transition:
                        existing_transition.transition_weight = float(row['transition_weight']) # type: ignore
                    else:
                        new_transition = Transition(
                            from_motif_id = from_motif.id,
                            to_motif_id = to_motif.id,
                            transition_weight = float(row['transition_weight'])
                        )
                        session.add(new_transition)

            session.commit()
            return {"status": "success", "message": "Transition(s) mapped successfully."}
        
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": f"Transition mapping failed: {str(e)}"}
        finally:
            session.close()
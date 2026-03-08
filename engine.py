import random
from database import DatabaseManager
from music21 import stream, note, chord, instrument, metadata, midi, tempo

class MusicEngine:
    """Converts raw SQL data into Music21 objects"""

    def __init__(self):
        """Initializes container for a musical composition"""
        self.score = stream.Score()
        self.parts = {} # Empty dictionary for active instrument tracks
        self.track_theory = {} # Stores scale data (scale_id and intervals) per track

    def initialize_tracks(self, track_rows, db_manager: DatabaseManager):
        """Maps SQL rows to music21 Part objects."""
        for row in track_rows:
            track_id = row['track_id']

            raw_name: str = row['track_name']
            track_name = raw_name.lower()

            scale_data = db_manager.fetch_scale_collection(row['scale_id'])
            self.track_theory[track_name] = {
                'intervals': [int(i) for i in scale_data['intervals'].split(',')],
                'root': scale_data['default_root_note'],
                'channel': row['midi_channel']
            }

            new_part: stream.Part = stream.Part()

            final_channel = 10 if "drums" in track_name or row['midi_channel'] == 10 else row['midi_channel']

            new_part.insert(0, instrument.Instrument(track_name))
            new_part.midiChannel = final_channel - 1

            self.parts[track_name] = new_part
            self.score.insert(0, new_part)
            print(f"--- TRACK READY: {track_name} assigned to {track_id} (Scale: {scale_data['scale_name']}) ---")

    def import_user_preferences(self, preferences: dict):
        """Sets the Tempo and Metadata based on SQL 'Constitution'."""
        # BPM - Uses .get() with a fallback to 120 if the key is missing from SQL
        bpm = int(preferences.get('default_bpm', 120))
        self.score.insert(0, tempo.MetronomeMark(number=bpm))

        # Metadata - Engraves the composition title into the MIDI file headers
        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = preferences.get('composition_title', 'Typebeat AI V7 Generated Score')

        print(f"--- Preferences: --- \n--- Default Tempo: {bpm} BPM | Title: {self.score.metadata.title} ---")

    def generate_song(self, db: DatabaseManager, genre_id, track_rows):
        """
        Translates the SQL blueprint into a Music21 score.
        """
        blueprint = db.fetch_song_blueprint(genre_id)
        current_offset = 0.0
        block_length = 4.0

        prev_motif = {t['track_id']: None for t in track_rows}

        for block in blueprint:
            target_class = block['block_class']

            for track in track_rows:
                track_id = track['track_id']
                track_name: str = track['track_name']
                track_name = track_name.lower()

                selected_data = self.select_motif(db, track_id, target_class, prev_motif[track_id])

                if selected_data:
                    motif_id = selected_data.get('to_motif_id') or selected_data.get('motif_id')
                    latency = float(selected_data.get('phrase_latency', 0.0))

                    self.generate_from_motif(
                        track_name, 
                        motif_id, 
                        db, 
                        offset=current_offset, 
                        phrase_latency=latency
                    )
                    prev_motif[track_id] = motif_id
                else:
                    prev_motif[track_id] = None
            
            current_offset += block_length # Advances to the next block

    def select_motif(self, db: DatabaseManager, track_id, target_class, current_id=None):
        """Unified selection engine: Handles both 'Opening' blocks and Markov transitions"""

        if current_id is not None:
            transitions = db.fetch_transitions(current_id)

            valid_transitions = [t for t in transitions if t.get('target_class') == target_class]

            if valid_transitions:
                weights = [t['weight'] for t in valid_transitions]
                return random.choices(valid_transitions, weights=weights, k=1)[0]
            
        pool = db.fetch_motifs(track_id, motif_class=target_class)

        if not pool:
            print(f"--- ERROR: No motifs found for class '{target_class} on track {track_id} ---")
            return None

        weights = [m.get('motif_weight', 1.0) for m in pool]
        return random.choices(pool, weights=weights, k=1)[0]

    def generate_from_motif(self, track_name, motif_id, db: DatabaseManager, offset=0, phrase_latency=0.0):
        """
        Fetches motif-specific note data and maps it onto a track
        Accommodates for transposition and musical entropy
        """
        note_details = db.fetch_motif_details(motif_id)
        motif_theory = self.track_theory[track_name]
        target_part: stream.Part = self.parts[track_name]

        chord_grouping: dict[tuple, list] = {}
        for note_set in note_details:
            # Key: Combination of beat position and chord_id to find harmonic stacks
            key = (note_set['beat_position'], note_set.get('chord_id'))
            if key not in chord_grouping:
                chord_grouping[key] = []
            chord_grouping[key].append(note_set)

        for (beat_position, _), stack in chord_grouping.items():
            stack: list[dict] = stack
            # Apply Scale-Aware Transposition
            pitches = []
            
            for n in stack:
                raw_pitch = n['pitch_value']
                pitches.append(motif_theory['root'] + raw_pitch if motif_theory['channel'] != 10 else raw_pitch)

            if len(pitches) > 1:
                new_element = chord.Chord(pitches)
            else:
                new_element = note.Note(pitches[0])
            
            final_position = offset + float(beat_position) + float(stack[0].get('micro_offset', 0)) + phrase_latency
            new_element.quarterLength = float(stack[0]['duration'])

            target_part.insert(final_position, new_element)


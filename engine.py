import random
from database import DatabaseManager
from music21 import stream, note, chord, instrument, metadata, midi, tempo

class MusicEngine:
    """Converts raw SQL data into Music21 objects"""

    def __init__(self):
        """Initializes container for a musical composition"""
        self.score = stream.Score() # Initialize "score" container object from Music21 library
        self.parts = {}             # Empty dictionary for active instrument tracks
        self.track_theory = {}      # Stores scale data (scale_id and intervals) per track

    def initialize_tracks(self, track_rows, db_manager: DatabaseManager):
        """Maps SQL rows to music21 Part objects."""
        
        for row in track_rows:
            # Track data assignment - Ensures data is taken from their respective columns collected from 'fetch_track_data' function 
            track_id = row['track_id']
            raw_name: str = row['track_name']
            track_name = raw_name.lower() # Converted to lower case for case insensitivity check when mapping to MIDI objects

            # Scale theory assignment - Initializes key-value pairings of track data collected from 'fetch_scale_collection' function
            scale_data = db_manager.fetch_scale_collection(row['scale_id'])
            self.track_theory[track_name] = {
                'intervals': [int(i) for i in scale_data['intervals'].split(',')],  # Consolidates every interval value from a scale into a sequential list while removing separator values (',') from the original string
                'root': scale_data['default_root_note'],                            # Starting 'MIDI pitch value' for a scale
                'channel': row['midi_channel']                                      # Dedicated MIDI channel to apply scale
            }

            new_part: stream.Part = stream.Part() # Initializes 'Part()' object from Music21 library

            # Drums assignment - Sets the dedicated MIDI channel with a two-way condition based on whether the track is 'Drums', or any other instrument
            final_channel = 10 if "drums" in track_name or row['midi_channel'] == 10 else row['midi_channel']
            new_part.insert(0, instrument.Instrument(track_name))   # Maps the track to an 'Instrument()' object from Music21 library
            new_part.midiChannel = final_channel - 1                # Follows General MIDI procedure, assigns 'Drums' the dedicated MIDI Channel 9

            # Base instrument assignment - Sets the dedicated MIDI channel and prints a success to the user
            self.parts[track_name] = new_part
            self.score.insert(0, new_part)
            print(f"--- TRACK READY: {track_name} assigned to {track_id} (Scale: {scale_data['scale_name']}) ---")

    def import_user_preferences(self, preferences: dict):
        """Sets the Tempo and Metadata based on SQL 'Constitution'."""

        # BPM assignment - Uses .get() with a fallback to 120 if the key is missing from SQL
        bpm = int(preferences.get('default_bpm', 120))
        self.score.insert(0, tempo.MetronomeMark(number=bpm))

        # Metadata assignment - Engraves the composition title into the MIDI file headers
        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = preferences.get('composition_title', 'Typebeat AI V7 Generated Score')

        print(f"--- Preferences: --- \n--- Default Tempo: {bpm} BPM | Title: {self.score.metadata.title} ---")

    def generate_song(self, db: DatabaseManager, genre_id, track_rows):
        """Translates the SQL blueprint into a Music21 score."""

        # Song structure assignment - Initializes specific song blueprint, starting offset, and song "Block" (Container for a Motif) length
        blueprint = db.fetch_song_blueprint(genre_id)
        current_offset = 0.0
        block_length = 4.0

        prev_motif = {t['track_id']: None for t in track_rows} # Dictionary comprehension uses placeholder consolidation to pair track IDs with empty values, creating a 'Skeleton Map'

        # Iterates through each motif container, mapping a generated motif while applying a set of constraints consistent with song blueprint
        for block in blueprint:
            # Initializes song block
            target_class = block['block_class']

            # Maps a motif to each available track
            for track in track_rows:
                track_id = track['track_id']
                track_name: str = track['track_name']
                track_name = track_name.lower() # Converted to lower case for case insensitivity check when mapping to MIDI objects

                selected_data = self.select_motif(db, track_id, target_class, prev_motif[track_id]) # Selects a motif for the designated track using Markov-based logic

                # Motif assignment - Applies all musical data from selected motif onto the designated track
                if selected_data:
                    motif_id = selected_data.get('to_motif_id') or selected_data.get('motif_id')    # Uses 'motif_id' as a default value if a transition to a new motif is not found
                    latency = float(selected_data.get('phrase_latency', 0.0))                       # Initializes phrase latency (Accommodates for Motif-Level human timing)

                    self.generate_from_motif(
                        track_name, 
                        motif_id, 
                        db, 
                        offset=current_offset, 
                        phrase_latency=latency
                    )
                    prev_motif[track_id] = motif_id
                else:
                    prev_motif[track_id] = None # Naturally exits the function if no motif ID can be selected
            
            current_offset += block_length # Advances to the next block

    def select_motif(self, db: DatabaseManager, track_id, target_class, current_id=None):
        """Unified selection engine: Handles both 'Opening' blocks and Markov transitions"""

        # Transition assignment - Searches for potential transitions relating to a motif class; groups them into a list and selects one based on its weighting
        if current_id is not None:
            transitions = db.fetch_transitions(current_id)

            valid_transitions = [t for t in transitions if t.get('target_class') == target_class] # Consolidates available transitions of a motif class into a list

            # If a list of valid transitions exists, consolidates weighting of each transition into a separate list and applies a motif with the randomly selected weighting
            if valid_transitions:
                weights = [t['weight'] for t in valid_transitions]
                return random.choices(valid_transitions, weights=weights, k=1)[0] # Selects the first piece of data from the single-item selection of weighting values

        # "Opening Block" assignment - Always selects from the list of available motifs relating to the first 'block_class' of the designated "Song Blueprint" (Which has to be the "Opening Block")
        pool = db.fetch_motifs(track_id, motif_class=target_class)

        if not pool:
            print(f"--- ERROR: No motifs found for class '{target_class} on track {track_id} ---")
            return None # Exits function if no motifs are found for the "Opening" motif class

        weights = [m.get('motif_weight', 1.0) for m in pool]
        return random.choices(pool, weights=weights, k=1)[0]

    def generate_from_motif(self, track_name, motif_id, db: DatabaseManager, offset=0, phrase_latency=0.0):
        """
        Fetches motif-specific note data and maps it onto a track
        Accommodates for transposition and musical entropy
        """

        # Macro-level initialization - Assigns motif data, scale data, and track data
        note_details = db.fetch_motif_details(motif_id)
        motif_theory = self.track_theory[track_name]
        target_part: stream.Part = self.parts[track_name]

        # Chord Initialization - Groups individual notes into harmonic stacks (Chord objects) based on time and ID
        chord_grouping: dict[tuple, list] = {}
        for note_set in note_details:
            # Key: Combination of beat position and chord_id to find harmonic stacks
            key = (note_set['beat_position'], note_set.get('chord_id'))
            # Assigns stack of notes as an entry to the list of initialized chords if they didn't previously exist
            if key not in chord_grouping:
                chord_grouping[key] = []
            chord_grouping[key].append(note_set)

        # Note initialization - Iterates through every chord grouping and maps their REQUIRED 'key' information (Only beat_position here) to a MIDI object
        # 'chord_grouping' is a universal container for all chord and non-chord-related notes alike, 'stack' is the collection of information regarding each note
        for (beat_position, _), stack in chord_grouping.items():
            stack: list[dict] = stack   # Contextualizes stack of notes as a list of dictionaries pertaining to musical data
            pitches = []                # Apply Scale-Aware Transposition
            
            # Transposition assignment - Applies note-level transposition using pitch values from 'motif_notes' table
            for n in stack:
                raw_pitch = n['pitch_value']
                pitches.append(motif_theory['root'] + raw_pitch if motif_theory['channel'] != 10 else raw_pitch) # Preserves pitch of 'Drums' MIDI channel, otherwise applies pitch value

            # MIDI object creation - If more than one value is detected in list of pitches, create a chord MIDI object. Else, create a note MIDI object
            if len(pitches) > 1:
                new_element = chord.Chord(pitches)
            else:
                new_element = note.Note(pitches[0])
            
            # Final timing assignment - Combines starting offset of motif, the note's beat position, and human timing at both a note and motif-level to find the final temporal position of the MIDI object
            final_position = offset + float(beat_position) + float(stack[0].get('micro_offset', 0)) + phrase_latency
            new_element.quarterLength = float(stack[0]['duration']) # Grabs the "note duration" of the first property taken from the stack

            target_part.insert(final_position, new_element)

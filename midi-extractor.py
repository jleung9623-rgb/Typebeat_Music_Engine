import mido
import pandas as pd
from database import DatabaseManager

class MidiIngester:
    def __init__(self, db_manager):
        self.db = db_manager
        self.ticks_per_beat = 480 # Standard MIDI resolution

    def process_file(self, file_path, genre_name, track_id, motif_class):
        """Extracts notes and calculates micro-timing for a single MIDI file."""
        mid = mido.MidiFile(file_path)
        self.ticks_per_beat = mid.ticks_per_beat
        
        notes = []
        current_tick = 0
        
        for track in mid.tracks:
            for msg in track:
                current_tick += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Convert ticks to musical beat positions
                    exact_beat = current_tick / self.ticks_per_beat
                    grid_beat = round(exact_beat * 4) / 4 # Quantize to 16th note grid
                    
                    # The difference is our human-performance 'micro_offset' [cite: 2026-03-04]
                    micro_offset = exact_beat - grid_beat
                    
                    notes.append({
                        'pitch_value': msg.note,
                        'beat_position': grid_beat,
                        'micro_offset': micro_offset,
                        'duration': 0.25 # Simplified for initial ingest
                    })

        # Create the DataFrame for the bulk_import method we verified earlier [cite: 2026-03-04]
        df = pd.DataFrame(notes)
        df['motif_name'] = file_path.split('/')[-1]
        df['genre_name'] = genre_name
        df['track_id'] = track_id
        df['motif_class'] = motif_class
        
        # Pass to the existing database logic [cite: 2026-03-03]
        return self.db.process_user_upload_from_df(df)

    def map_transitions(self, motif_sequence):
        """
        Analyzes a sequence of motifs to populate the Markov transitions table.
        Input: List of motif_ids in the order they appeared in a song.
        """
        for i in range(len(motif_sequence) - 1):
            from_id = motif_sequence[i]
            to_id = motif_sequence[i+1]
            
            # SQL logic: INSERT ... ON DUPLICATE KEY UPDATE weight = weight + 1 [cite: 2026-03-03]
            self.db.increment_transition(from_id, to_id)
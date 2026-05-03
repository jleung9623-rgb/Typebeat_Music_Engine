import mido
import pandas as pd
import os
import re
import math
from database.models import SectionClass

class MidiExtractor:
    def __init__(self, min_velocity=20):
        """Initializes relevant note-level MIDI data."""
        self.ticks_per_beat = 480 # Standard MIDI resolution
        self.min_velocity = min_velocity

    def extract_midi_data(self, file_path: str, output_dir: str ="extracted_csvs"):
        """Extracts notes from a MIDI file and saves them into a CSV format."""
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(file_path)

        # Parses the section classification from the filename using regex, expecting the pattern: "FILENAME-CLASSNAME.mid"
        match = re.search(r'-([A-Za-z_]+)\.mid$', filename)
        if not match:
            return {"status": "error", "message": f"Filename {filename} does not match expected pattern for section classification. Must end with -CLASSNAME.mid"}
        
        # Scans the file name until it backtraces to the last hyphen, then captures the subsequent string as the class name, converting it to uppercase for standardization
        parsed_class = match.group(1).upper()

        # Validates schema against Live Database Enums
        valid_classes = [item.value.upper() for item in SectionClass]
        if parsed_class not in valid_classes:
            return {"status": "error", "message": f"Parsed class '{parsed_class}' from filename {filename} is not a valid SectionClass Enum."}

        target_class = parsed_class.title() if parsed_class != "FX" else "FX"

        try:
            mid = mido.MidiFile(file_path)
            self.ticks_per_beat = mid.ticks_per_beat

            notes = []
            active_notes = {}
            current_tick = 0

            # Iterates through each track in MIDI file, extracting note data
            for track in mid.tracks:
                current_tick = 0

                for midi_event in track:
                    current_tick += midi_event.time
                    exact_beat = current_tick / self.ticks_per_beat

                    if midi_event.type == 'note_on' and midi_event.velocity >= self.min_velocity:
                        grid_beat = round(exact_beat * 4) / 4
                        micro_offset = exact_beat - grid_beat
                        active_notes[midi_event.note] = (exact_beat, grid_beat, micro_offset)

                    elif midi_event.type == 'note_off' or (midi_event.type == 'note_on' and midi_event.velocity == 0):
                        if midi_event.note in active_notes:
                            ex_beat_ss, grid_beat_ss, m_offset_ss = active_notes.pop(midi_event.note) # Grabs a snapshot of the activation timing of designated note
                            duration_beats = exact_beat - ex_beat_ss

                            notes.append({
                                'pitch_value': midi_event.note,
                                'beat_position': grid_beat_ss,
                                'duration': round(duration_beats, 3),
                                'micro_offset': round(m_offset_ss, 3)
                            })

            if not notes:
                return {"status": "error", "message": f"No notes passed velocity threshold (>{self.min_velocity}) in {file_path}"}
            
            # Ensures the flat list is strictly ordered chronologically by beat position
            notes.sort(key=lambda x: x['beat_position'])

            SILENCE_GAP_BEATS = 2.0     # Number of beats of silence that automatically triggers the start of a new motif
            MAX_MOTIF_BEATS = 4.0       # Hard constraint for maximum motif length
            GRID_RESOLUTION = 1.0       # Snaps grid boundaries to nearest quarter note

            segmented_rows = []
            current_motif_notes = []
            motif_counter = 1

            current_motif_start = notes[0]['beat_position']
            highest_beat_end = 0.0

            for note in notes:
                beat_position = note['beat_position']
                duration = note['duration']

                silence_detected = (beat_position - highest_beat_end) >= SILENCE_GAP_BEATS
                length_exceeded = (beat_position - current_motif_start) >= MAX_MOTIF_BEATS

                if (silence_detected or length_exceeded) and current_motif_notes:
                    # Calculates the physical end of the active chunk
                    last_beat = max((n['beat_position'] + n['duration']) for n in current_motif_notes)

                    # Calculates the distance to the next grid boundary
                    grid_boundary = math.ceil(last_beat / GRID_RESOLUTION) * GRID_RESOLUTION
                    rest_duration = round(grid_boundary - last_beat, 3)

                    # Generates the rest tag for the static library
                    rest_tag = f"REST_{rest_duration}" if rest_duration > 0 else "NONE"

                    # Logs the pivot offset for the motif
                    pivot_offset = round(last_beat, 3)

                    # Appends mapped notes to the segmented master list
                    for n in current_motif_notes:
                        n['motif_name'] = f"{os.path.basename(file_path).split('.')[0]}_M{motif_counter}"
                        n['motif_class'] = target_class
                        n['motif_pivot_offset'] = pivot_offset
                        n['rest_duration'] = rest_duration
                        n['rest_suffix'] = rest_tag
                        segmented_rows.append(n)

                    # Resets accumulators for the next motif chunk
                    current_motif_notes = []
                    motif_counter += 1
                    current_motif_start = beat_position

                # Calculates the absolute grid start of the current motif chunk
                chunk_grid_start = math.floor(current_motif_start / GRID_RESOLUTION) * GRID_RESOLUTION

                # Calculates the leading silence before the first note of the motif chunk
                phrase_latency = round(current_motif_start - chunk_grid_start, 3)

                # Normalizes note timing to 0.0 for the current chunk
                normalized_beat = round(beat_position - current_motif_start, 3)

                current_motif_notes.append({
                    'pitch_value': note['pitch_value'],
                    'beat_position': normalized_beat,
                    'duration': duration,
                    'micro_offset': note['micro_offset'],
                    'phrase_latency': phrase_latency
                })

                highest_beat_end = max(highest_beat_end, beat_position + duration)

            # Flushes the final motif chunk if it exists, applying the same logic as above for rest tagging and pivot offset
            if current_motif_notes:
                last_beat = max((n['beat_position'] + n['duration']) for n in current_motif_notes)
                grid_boundary = math.ceil(last_beat / GRID_RESOLUTION) * GRID_RESOLUTION
                rest_duration = round(grid_boundary - last_beat, 3)
                rest_tag = f"REST_{rest_duration}" if rest_duration > 0 else "NONE"
                pivot_offset = round(last_beat, 3)

                for n in current_motif_notes:
                    n['motif_name'] = f"{os.path.basename(file_path).split('.')[0]}_M{motif_counter}"
                    n['motif_class'] = target_class
                    n['motif_pivot_offset'] = pivot_offset
                    n['rest_duration'] = rest_duration
                    n['rest_suffix'] = rest_tag
                    n['phrase_latency'] = phrase_latency
                    segmented_rows.append(n)

            # Structures the DataFrame to align with the expected format for the CSV Upload pipeline
            df = pd.DataFrame(segmented_rows)
            df = df[['motif_name', 'motif_class', 'motif_pivot_offset', 'rest_duration','rest_suffix', 'phrase_latency', 'pitch_value', 'beat_position', 'duration', 'micro_offset']]

            base_name = os.path.basename(file_path).replace('.mid', '.csv')
            output_csv_path = os.path.join(output_dir, base_name)
            df.to_csv(output_csv_path, index=False)

            return {"status": "success", "message": f"Extracted {len(df)} notes into {motif_counter} motifs.", "path": output_csv_path}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def batch_process_folder(self, input_folder, output_folder='extracted_csvs'):
        """Processes an entire folder of MIDI files into CSV-formatted note data."""
        files = [f for f in os.listdir(input_folder) if f.endswith('.mid')]
        results = []

        print(f"--- Starting Batch Extraction: {len(files)} files ---")

        for f in files:
            full_path = os.path.join(input_folder, f)
            output = self.extract_midi_data(full_path, output_folder)
            results.append(output)
            print(f"Processed {f}: {output['status']}")

        return results
    
if __name__ == "__main__":
    extractor = MidiExtractor(min_velocity=25)
    folder_path = input("Enter path to MIDI folder: ").strip()

    if os.path.isdir(folder_path):
        extractor.batch_process_folder(folder_path)
    else:
        print("Invalid directory.")
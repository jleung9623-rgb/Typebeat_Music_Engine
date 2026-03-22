import mido
import pandas as pd
import os

class MidiExtractor:
    def __init__(self, min_velocity=20):
        """Initializes relevant note-level MIDI data"""
        
        self.ticks_per_beat = 480 # Standard MIDI resolution
        self.min_velocity = min_velocity # Minimum velocity value used to filter out quieter notes

    def extract_midi_data(self, file_path: str, output_dir: str ="extracted_csvs"):
        """Extracts notes from a MIDI file and saves them into a CSV format."""

        os.makedirs(output_dir, exist_ok=True) # Creates 'extracted_csvs' directory for output files

        try:
            mid = mido.MidiFile(file_path) # Initializes the MIDI file "container" that will be used for note data extraction
            self.ticks_per_beat = mid.ticks_per_beat
            
            notes = []          # Will track full list of notes in MIDI file
            active_notes = {}   # Will track when notes turn on to calculate duration
            current_tick = 0
            
            # Iterates through each track in MIDI file, extracting note data and filtering ineligible note properties
            for track in mid.tracks:
                current_tick = 0 # Reset tick counter for each track

                # Calculates the exact beat of each MIDI event (Activation/Deactivation of notes)
                for midi_event in track:
                    current_tick += midi_event.time # Accumulate delta time (Adhering to Mido standards)
                    exact_beat = current_tick / self.ticks_per_beat # Uses delta time to calculate the exact beat of each note

                    # Identifies note activations that meet the minimum velocity threshold
                    if midi_event.type == 'note_on' and midi_event.velocity >= self.min_velocity:
                        grid_beat = round(exact_beat * 4) / 4   # Quantizes to 16th note grid
                        micro_offset = exact_beat - grid_beat   # Calculates temporal deviation from beat grid

                        # Consolidates collection of timing data into a note entry
                        active_notes[midi_event.note] = (exact_beat, grid_beat, micro_offset)

                    # Identifies and calculates note deactivations using active_notes dictionary
                    elif midi_event.type == 'note_off' or (midi_event.type == 'note_on' and midi_event.velocity == 0):
                        if midi_event.note in active_notes:
                            # Grabs a snapshot of the activation timing of designated note
                            ex_beat_ss, grid_beat_ss, m_offset_ss = active_notes.pop(midi_event.note)
                            
                            # Calculates note duration
                            duration_beats = exact_beat - ex_beat_ss 

                            # Adds final data to list of MIDI-eligible notes
                            notes.append({
                                'pitch_value': midi_event.note,
                                'beat_position': grid_beat_ss,
                                'duration': round(duration_beats, 3),
                                'micro_offset': round(m_offset_ss, 3)
                            })

            # Checks if final MIDI-eligible notes exist
            if not notes:
                return {"status": "error", "message": f"No notes passed velocity threshold (>{self.min_velocity}) in {file_path}"}
            
            # Initializes Pandas DataFrame for CSV upload
            df = pd.DataFrame(notes)

            # Replaces the destination file extension with '.csv'
            base_name = os.path.basename(file_path).replace('.mid', '.csv')

            # Links save path to the previously created output directory
            output_csv_path = os.path.join(output_dir, base_name)

            # Establishes DataFrame as a CSV file and returns success protocol for the user
            df.to_csv(output_csv_path, index=False)
            return {"status": "success", "message": f"Extracted {len(df)} notes.", "path": output_csv_path}
        
        # Checks if any outstanding errors occurred during the MIDI note extraction process
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def batch_process_folder(self, input_folder, output_folder="extracted_csvs"):
        """Processes an entire folder of MIDI files into CSV-formatted note data."""

        # Consolidates list of all eligible MIDI files and initializes container for final output
        files = [f for f in os.listdir(input_folder) if f.endswith('.mid')]
        results = []

        print(f"--- Starting Batch Extraction: {len(files)} files ---")

        # Iterates through each MIDI file, extracting note data and appending it to final arrangement
        for f in files:
            full_path = os.path.join(input_folder, f)
            res = self.extract_midi_data(full_path, output_folder)
            results.append(res)
            print(f"Processed {f}: {res['status']}")

        return results
        
if __name__ == "__main__":
    extractor = MidiExtractor(min_velocity=25)

    # Prompts user for path to existing MIDI files
    folder_path = input("Enter path to MIDI folder: ").strip()

    # If path exists, execute the batch extraction process before saving the CSV file into the output directory
    if os.path.isdir(folder_path):
        extractor.batch_process_folder(folder_path)
    else:
        print("Invalid directory.") # Prints an error if the source MIDI folder path is invalid
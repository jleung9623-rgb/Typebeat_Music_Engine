import os
import csv
import random
from database.models import SectionClass, Track
from data_inflow.motifs_upload import MotifUploader
from database.connection import SessionLocal


def create_mock_motif_batch():
    BATCH_SIZE = 50
    TEMP_CSV_PATH = "data/sample_data/temp_stress_test_motif.csv"
    
    # Initializes a local database session to query for valid track IDs to associate with the mock motif batch, selecting one at random for the upload process.
    session = SessionLocal()
    try:
        valid_tracks = session.query(Track).all()
        valid_track_ids = [track.id for track in valid_tracks]

        if not valid_track_ids:
            raise ValueError("Tracks table is empty. Tracks must be seeded before generating Motifs.")
        
    finally:
        session.close()

    for TARGET_TRACK_ID in valid_track_ids:
        # Creates the temporary output path for the CSV batch file
        os.makedirs(os.path.dirname(TEMP_CSV_PATH), exist_ok=True)

        print(f"Generating motif batch CSV for {BATCH_SIZE} motifs...")

        # Initialize list of eligible motif classes based on Enum labels
        section_classes = list(SectionClass)

        # Opens the CSV file in 'write' mode, adding a dummy sequence of notes to rows pertaining to each mock motif
        with open(TEMP_CSV_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['motif_name', 'motif_class', 'pitch_value', 'beat_position', 'duration'])

            for i in range(BATCH_SIZE):
                m_name = f"STRESS_TEST_{i}"
                m_class = random.choice(section_classes).value # Song structure blocks are selected at random

                writer.writerow([m_name, m_class, random.randint(60, 72), 0.0, 1.0])
                writer.writerow([m_name, m_class, random.randint(60, 72), 1.0, 1.0])
                writer.writerow([m_name, m_class, random.randint(60, 72), 2.0, 1.0])
                writer.writerow([m_name, m_class, random.randint(60, 72), 3.0, 1.0])
        
        print("CSV generation complete. Passing to CSVUploader pipeline...")

        # Initializes path to Motif CSV Uploader, designating the required information needed to upload the mock motif batch
        uploader = MotifUploader()
        result = uploader.upload_batch(
            csv_file_path = TEMP_CSV_PATH,
            track_id = TARGET_TRACK_ID
        )

        if result['status'] == 'success':
            print(result['message'])
        else:
            print(f"Pipeline failure: {result['message']}")
        
        # Deletes the temporary file so leftover data doesn't corrupt the next test.
        if os.path.exists(TEMP_CSV_PATH):
            os.remove(TEMP_CSV_PATH)

if __name__ == "__main__":
    create_mock_motif_batch()
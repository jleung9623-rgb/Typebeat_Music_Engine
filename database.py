import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from typing import TYPE_CHECKING

# Initializes ability to contextualize and label functions specific to 'pandas' library
if TYPE_CHECKING:
    import pandas as pd

class DatabaseManager:
    """Handles all communication with the MySQL database"""

    def __init__(self, host='localhost', user='root', database='typebeat_ai_v7'):
        # Load .env file into the environment, overrides system defaults for security
        load_dotenv(override=True)
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "typebeat_ai_v7")

        print(f"--- Logging in as '{db_user}' ---")

        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name
            )
            if self.connection.is_connected():
                print(f"--- SUCCESS: Established connection with {db_name} ---")
        # Error recognition for SQL-side initialization and connection errors
        except Error as e:
            print(f"--- ERROR: Could not connect to database: {e} ---")
            exit()
    
    def fetch_user_preferences(self):
        """Fetches the EAV Key-Value pairs and converts them to a Python Dictionary."""

        query = "SELECT setting_key, setting_value FROM user_preferences"
        # Across all fetch functions, ensures memory allocated within try/except block is automatically freed regardless of outcome
        # Implemented to prevent cursor initialization overlap, connection limits, and memory leaks
        try:
            with self.connection.cursor(dictionary=True) as cursor: # Initializes a "Contextualized Variable" that automatically frees itself once the code block completes.
                cursor.execute(query)       # Executes query
                rows = cursor.fetchall()    # Fetches all data in the rows the cursor is pointing at

                # Dictionary Comprehension used to convert the list of user_preferences rows (Also dictionaries) into a consolidated dictionary
                # e.g., {'default_bpm': '145', 'active_genre': 'Pop-Punk'}
                return {row['setting_key']: row['setting_value'] for row in rows}
        except Error as e:
            print(f"--- ERROR: Failed to fetch user preferences: {e}")
            return {} # Returns an empty element of the required data type (Dictionary in this case)
    
    def fetch_song_blueprint(self, genre_id):
        """
        Import song structure layouts "Blueprints" (e.g. "Intro > Verse > Build > Chorus > Rest > etc.")
        Retrieves the exact block sequence for the active genre
        """

        query = """
            SELECT block_position, block_class
            FROM song_blueprints
            WHERE genre_id = %s
            ORDER BY block_position ASC
        """
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (genre_id, ))
                return cursor.fetchall()
        except Error as e:
            print(f"Failed to fetch song structure: {e}")
            return [] # Returns an empty element of the required data type (List in this case)
    
    def fetch_track_data(self, genre_name):
        """Fetches all MIDI instruments associated with a specific genre"""

        query = """
            SELECT t.track_id, t.track_name, t.instrument_name, 
                   t.midi_channel, t.patch_number, t.scale_id, t.track_motif_limit
            FROM tracks AS t
            JOIN genres AS g ON t.genre_id = g.genre_id
            WHERE g.genre_name = %s
        """
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (genre_name,))
                return cursor.fetchall()
        except Error as e:
            print(f"Failed to fetch track data: {e}")
            return []
    
    def fetch_scale_collection(self, scale_id):
        """Fetches the mathematical intervals and root note for a specific scale"""

        query = "SELECT scale_name, intervals, default_root_note FROM scales WHERE scale_id = %s"
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (scale_id, ))
                return cursor.fetchone()
        except Error as e:
            print(f"--- ERROR: Failed to fetch scale logic: {e}")
            return None
    
    def fetch_transitions(self, from_motif_id):
        """Fetches the Markov Chain data as the foundation for the AI's decision-making"""

        query = """
            SELECT t.to_motif_id, t.weight, m.motif_class AS target_class
            FROM transitions AS t
            JOIN motifs AS m ON t.to_motif_id = m.motif_id
            WHERE t.from_motif_id = %s
            ORDER BY t.weight DESC
        """
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (from_motif_id, ))
                return cursor.fetchall()
        except Error as e:
            print(f"--- ERROR: Failed to fetch motif transitions: {e}")
            return[]
    
    def fetch_motifs(self, track_id, motif_class=None):
        """Fetches all curated motifs for the specified track. Additionally filters by "Class" of motif (Chorus, Bridge, etc.)"""

        query = """
            SELECT motif_id, motif_name, sequence_data, 
                   motif_pivot_offset, phrase_latency, motif_class
            FROM motifs
            WHERE track_id = %s
        """
        track_container = [track_id] # Temp container for track_id to accommodate for conditional variation logic

        # Add 'motif_class' as an additional property of the original query and appends it to the list of elements related to 'track_id'
        if motif_class:
            query += " AND motif_class = %s"
            track_container.append(motif_class)

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(track_container))
                return cursor.fetchall()
        except Error as e:
            print(f"--- ERROR: Failed to fetch motifs: {e}")
            return []
    
    def fetch_motif_details(self, motif_id):
        """
        Fetches high-definition musical data for a specific motif.
        Handshake: Uses 'motif_id' to bridge the motifs table to motif_notes.
        """

        query = """
            SELECT pitch_value, duration, beat_position, micro_offset, chord_id
            FROM motif_notes
            WHERE motif_id = %s
            ORDER BY beat_position ASC
        """
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (motif_id,))
                return cursor.fetchall()
        except Error as e:
            print(f"--- ERROR: Failed to fetch motif details for ID {motif_id}: {e} ---")
            return []
    
    def fetch_chord_library(self):
        """Fetches the musical data of every chord type and their related notes in the database"""

        query = """
            SELECT c.chord_id, c.chord_name, cn.note_name
            FROM chords AS c
            JOIN chord_notes AS cn ON c.chord_id = cn.chord_id
        """
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query) # Placeholders omitted from this query
                return cursor.fetchall()
        except Error as e:
            print(f"--- ERROR: Failed to fetch chord library: {e}")
            return []
        
    def process_user_upload(self, csv_file_path: str):
        """Initializes set of required fields of data to be uploaded to SQL database"""

        import pandas as pd # Locally imports 'pandas'; keeps data inflow to csv-specific functions
        
        df = pd.read_csv(csv_file_path)     # Initializes dataframe by reading the CSV file at 'csv_file_path' with pandas
        df.columns = df.columns.str.strip() # Clean up whitespace in column names to prevent false 'Missing Column' errors

        # Designates list of essential columns for data to be uploaded to
        required = [
            'motif_name', 'genre_name', 'track_id', 'chord_id',
            'motif_class', 'pitch_value', 'duration', 'beat_position'
        ]
        
        # Sets default values for non-required fields if there was no data uploaded into them
        if 'micro_offset' not in df.columns:
            df['micro_offset'] = 0.0
        if 'phrase_latency' not in df.columns:
            df['phrase_latency'] = 0.0
        if 'motif_pivot_offset' not in df.columns:
            df['motif_pivot_offset'] = 0.0
        if 'motif_weight' not in df.columns:
            df['motif_weight'] = 1.0

        # Returns an error if data being appended to a required column does not exist
        if not all(col in df.columns for col in required):
            missing = [c for c in required if c not in df.columns]
            return {"status": "error", "message": f"CSV missing essential data: {missing}"}

        return self.bulk_import(df)
    
    def bulk_import(self, df: 'pd.DataFrame'):
        """
        Executes direct Motif -> Motif Note mapping.
        Prioritizes track-specific note assignment.
        """

        import pandas as pd
        chosen_df: pd.DataFrame = df # Assigns the pandas 'DataFrame' label to the parameter 'df'; validates that data type within Python

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                row = chosen_df.iloc[0] # Assigns the information from the location of the CSV file's first row (As a single element from the pandas 'DataFrame')

                cursor.execute("INSERT IGNORE INTO genres (genre_name) VALUES (%s)", (row['genre_name'], ))
                cursor.execute("SELECT genre_id FROM genres WHERE genre_name = %s", (row['genre_name'], ))

                cursor.execute("""
                    INSERT INTO motifs (track_id, motif_name, motif_class, 
                                    motif_pivot_offset, phrase_latency, motif_weight)
                    VALUES (%s, %s, %s, %s, %s, %s)           
                """, (
                    int(row['track_id']),
                    row['motif_name'],
                    row['motif_class'],
                    row.get('motif_pivot_offset', 0.0),
                    row.get('phrase_latency', 0.0),
                    row.get('motif_weight', 1.0)
                ))

                motif_id = cursor.lastrowid # Assigns the last row id (Auto-Incremented element from MySQL Connector) to motif id

                sequence_token = f"M{motif_id}_T{row['track_id']}_{row['motif_class'][:3].upper()}" # Processes the token 'Taxonomy Label' for the motif sequence data
                cursor.execute("UPDATE motifs SET sequence_data = %s WHERE motif_id = %s", (sequence_token, motif_id))

                query = """
                    INSERT INTO motif_notes (motif_id, pitch_value, duration, beat_position, micro_offset, chord_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                # Consolidates data from required upload fields into a sequential list
                note_data = [
                    (
                        motif_id,
                        r['pitch_value'],
                        r['duration'],
                        r['beat_position'],
                        r.get('micro_offset', 0.0),
                        r.get('chord_id') # Can be NULL for neutral motifs
                    )
                    for _, r in chosen_df.iterrows()
                ]
        
                cursor.executemany(query, note_data) # Executes the queries using each element of the note_data list as parameters, in sequential order

                self.connection.commit()

                # Acts as the "Receipt" of a successful CSV upload; visual indicator for users and future parameters for function calls in main
                return {
                    "status": "success",
                    "motif_id": motif_id,
                    "sequence_token": sequence_token,
                    "note_count": len(note_data)
                }
        except Exception as e:
            self.connection.rollback() # Reverts the SQL database to the state before function was initiated (Does keep implicit record of table 'incremental id' changes)
            print(f"--- DATABASE ERROR: Bulk Import Failed: {e} ---")
            return {"status": "error", "message": str(e)}
        
    def save_composition_record(self, file_name, file_path, artist_id=1):
        """Utilizes the compositions table to save a record of the generated file."""

        # 'created_at' logs current time at the moment of this line's insertion into the database using 'NOW()'
        query = "INSERT INTO compositions (file_name, file_path, artist_id, created_at) VALUES (%s, %s, %s, NOW())"
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (file_name, file_path, artist_id))
                self.connection.commit()
                print(f"--- SUCCESS: {file_name} saved to Compositions Database ---")
        except Exception as e:
            print(f"--- ERROR: Failed to save composition {e} ---")

    # Disconnects from SQL Server
    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("--- SUCCESS: Connection terminated safely ---")
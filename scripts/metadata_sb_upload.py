import pandas as pd
from database.models import Artist, Genre, artist_genre_map, genre_track_map, genre_blueprint_map, Track, TrackClass, SongBlueprint, BlockClass
from database.connection import SessionLocal

class CSVUploader:
    def __init__(self):
        """Initializes list of required upload fields and switchboard selection outcomes"""

        # Temporary storage for existing genres (Used for `get_genre` function)
        self.genre_cache = {}

        # Dictionary for all upload requirement columns to be checked in `switchboard()`
        self.upload_requirements = {
            "artists": ['artist_name'],
            "genres": ['genre_name', 'default_tempo', 'time_signature'],
            "tracks": ['track_name', 'track_class', 'genre_name', 'midi_channel'],
            "blueprints": ['genre_name', 'block_class', 'block_position'],
        }

        # Initializes list of paths for upload handlers to be used in `upload_interface.py`
        self.handlers = {
            "artists": self.upload_artists,
            "genres": self.upload_genres,
            "tracks": self.upload_tracks,
            "blueprints": self.upload_blueprints
        }

    def switchboard(self, target, csv_file_path):
        """Creates a  single entry point for all upload functions to be selected from"""

        # Raises error if selected upload faculty does not exist
        handler = self.handlers.get(target.lower())
        if not handler:
            raise ValueError(f"Unknown faculty target: {target}")
        
        # Pandas Initialization - Dataframe & Columns
        df = pd.read_csv(csv_file_path)
        df.columns = df.columns.str.strip()

        # Upload Validation - Returns targeted errors if the user failed to adhere to CSV upload protocol
        required = self.upload_requirements.get(target)
        if required:
            missing = [col for col in required if col not in df.columns]
            if missing: # Returns error if required columns not found in user CSV, based on consolidated list of "missing" fields
                return {"status": "error", "message": f"Missing columns in {target} CSV: {missing}"}
            
            if df[required].isnull().values.any(): # Checks if any data exists in the DataFrame's columns
                return {"status": "error", "message": f"Empty required cells detected in {target} CSV."}
        
        print(f"--- Proceeding to '{target}' upload")

        # Session initialization - Performs a rollback if database error occurs, otherwise commits to an upload instance
        session = SessionLocal()
        try:
            result_message = handler(df, session)
            session.commit()
            return {"status": "success", "message": result_message}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": f"Database Error: {str(e)}"}
        finally:
            session.close() # Closes session upon completion
    
    # Independent Upload Functions (Metadata & Macro-Level Musical Constraints)

    def upload_artists(self, df, session):
        """Uploads Artist data through a CSV file, associate said data to a Genre in the process"""

        for _, row in df.iterrows():
            # Only returns the first available result matching an `Artist` instance
            artist = session.query(Artist).filter_by(artist_name=row['artist_name']).first()

            # Adds a new artist entry if it doesn't exist
            if not artist:
                artist = Artist(artist_name=row['artist_name'])
                session.add(artist)
                session.flush() # Syncs with DB before establishing junction table relationship

            # Checks if the artist entry has an associated genre based on CSV upload data. Creates a link to the specified one if it doesn't exist
            if 'genre_name' in row and pd.notna(row['genre_name']):
                # Grabs genre from current session instance's database
                genre = self.get_genre(row['genre_name'], session)

                # Initializes the relationship with a genre through an artist -> genre junction table
                if genre:
                    link = session.query(artist_genre_map).filter_by(
                        artist_id = artist.id,
                        genre_id = genre.id
                    ).first()

                    # If genre exists with no association to the artist, adds a link through the `artist_genre_map` junction table
                    if not link:
                        link_init = artist_genre_map.insert().values(
                            artist_id = artist.id,
                            genre_id = genre.id,
                            affinity_score = row.get('affinity_score', 1.0)
                        )
                        session.execute(link_init)

        return f"Successfully imported {len(df)} artists."

    def upload_genres(self, df, session):
        """Uploads Genre-level musical constraints through a CSV file"""

        # If genre doesn't exist, adds a new Genre entry with the required fields
        for _, row in df.iterrows():
            genre = session.query(Genre).filter_by(genre_name=row['genre_name']).first()
            if not genre:
                genre = Genre(
                    genre_name = row['genre_name'],
                    default_tempo = row['default_tempo'],
                    time_signature = row['time_signature']
                )
                session.add(genre)
                
        return f"Successfully imported {len(df)} genres."
    
    # Dependent Upload Functions (Requires Genre as a parent)

    def upload_tracks(self, df, session):
        """Uploads Instrument track musical constraints through a CSV file"""

        # Genre -> Track Relationship - Checks if genres exist before trying to initialize a track
        for _, row in df.iterrows():
            genre = self.get_genre(row['genre_name'], session)
            if not genre:
                print(f"ERROR: Genre '{row['genre_name']}' must be uploaded before its tracks.")
                continue

            # Adds a new track entry with the required fields
            track = session.query(Track).filter_by(track_name=row['track_name']).first()
            if not track:
                track = Track(
                    track_name = row['track_name'],
                    track_class = TrackClass[row['track_class'].upper()],
                    midi_channel = int(row['midi_channel']),
                    instrument_name = row.get('instrument_name'),
                    patch_number = int(row['patch_number']) if pd.notna(row.get('patch_number')) else None,
                    track_motif_limit = int(row['track_motif_limit']) if pd.notna(row.get('track_motif_limit')) else None
                )
                session.add(track)
                session.flush() # Syncs with DB before establishing junction table relationship
            
            # Initializes the relationship with a track through a genre -> track junction table
            link = session.query(genre_track_map).filter_by(
                genre_id = genre.id,
                track_id = track.id
            ).first()
            

            # If track exists with no association to the genre, adds a link through the `genre_track_map` junction table
            if not link:
                link_init = genre_track_map.insert().values(
                    genre_id = genre.id,
                    track_id = track.id,
                    selection_weight = row.get('selection_weight', 1.0)
                )
                session.execute(link_init)

        return f"Successfully imported {len(df)} tracks."

    def upload_blueprints(self, df, session):
        """Uploads song structure containers that serve to define the arrangement sequence of generated motifs"""
        
        # Genre -> Blueprint Relationship - Checks if genres exist before trying to initialize a blueprint block
        for _, row in df.iterrows():
            genre = self.get_genre(row['genre_name'], session)
            if not genre:
                print(f"ERROR: Genre '{row['genre_name']}' not found for blueprint block")
                continue

            # Selects the first unique blueprint entry detected based on both the block's class and temporal position within a song
            song_blueprint = session.query(SongBlueprint).filter_by(
                block_class=BlockClass[row['block_class'].upper()],
                block_position=row['block_position']
            ).first()

            # Adds a new blueprint entry with the required fields
            if not song_blueprint:
                song_blueprint = SongBlueprint(
                    block_class = BlockClass[row['block_class'].upper()],
                    block_position = row['block_position']
                )
                session.add(song_blueprint)
                session.flush() # Syncs with DB before establishing junction table relationship

            # Initializes the relationship with a blueprint through a genre -> blueprint junction table
            link = session.query(genre_blueprint_map).filter_by(
                genre_id = genre.id,
                blueprint_id = song_blueprint.id
            ).first()

             # If blueprint exists with no association to the genre, adds a link through the `genre_blueprint_map` junction table
            if not link:
                link_init = genre_blueprint_map.insert().values(
                    genre_id = genre.id,
                    blueprint_id = song_blueprint.id
                )
                session.execute(link_init)

        return f"Successfully imported {len(df)} blueprints blocks."
    
    def get_genre(self, name, session):
        """Creates a temporary storage of all available genres for faster indexing during upload functions"""
        
        # Returns genre_cache full of existing genre names if they exist, adds genre name to cache if it exists outside of the temp storage
        if name in self.genre_cache:
            return self.genre_cache[name]
        genre = session.query(Genre).filter_by(genre_name=name).first()
        if genre:
            self.genre_cache[name] = genre
        return genre

if __name__ == "__main__":
    engine = CSVUploader()
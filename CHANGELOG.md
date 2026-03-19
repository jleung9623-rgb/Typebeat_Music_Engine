#### [7.2.0-alpha] - 2026-03-14

#### Added
- SQLAlchemy ORM integration for all related tables.
- Alembic migration environment for version-controlled schema changes.
- CSV Upload and static music data seeding scripts (`harmonic_map.py`, `metadata_sb_upload.py`, `motifs_upload.py`).
- User interface for upload selection and routing.
- Added `__init__.py` initialization file

#### Changed
- SQL database connection initialization now isolated and deferred to `connection.py`
- Refactored `models.py` to use Declarative Base.
- Migration from raw SQL initialization to `alembic upgrade head`.
- Renamed database to `typebeat_ai`
- Updated `.env` requirements to include centralized DB_NAME.
- Seeded basic chord and scale data into database
- Segmented database and upload functions into specific faculties

#### Removed
- Legacy `database.py` raw SQL handlers.

#### [7.1.0-alpha] - 2026-03-11

#### **General**

* Separated the program files into `main.py`, `engine.py`, and `database.py`
* Added and adjusted new tables to the **SQL database** to support a more consistent inflow of data
* Added formal `main()` function in `main.py` to house the primary execution flow
* Imported **typing** library to contextualize syntax specific to the **pandas** library

#### **SQL Database Schema**

* Added new table `motif_notes`
* Added new table `song_blueprints`
* Created foreign key relationship between `motif_notes` and `chords` tables
* Moved `default_root_note` from `genres` to `scales` table
* Moved Markov logic columns from `transitions` to `motifs` table
* Added new musical data and metadata columns columns to `motifs` table
* Added `track_motif_limit` column to `tracks` table

#### **database.py**

* Added latent function `bulk_import()` to upload CSV files using the **pandas** library
* Added latent function `process_user_upload()` to initialize list of required fields from CSV files during upload to SQL Database
* Added function `save_composition_record()` to log user's saved composition record in the database's `compositions` table
* Added function `fetch_motif_details()` to collect high-definition data for a specific motif from database
* Added function `fetch_scale_collection()` to collect the scale intervals and root note for a specific scale from database
* Added function `fetch_song_blueprint()` to collect the song structure data to be mapped to a composition

#### **engine.py**

* Applied scale theory logic to `initialize_tracks()` function, accommodating track-level scale and interval data
* Renamed `generate_sequence()` function to `generate_song()` to accentuate motif-level transitions and integrate song blueprint constraints on engine
* Added function `select_motif()` to handle transitions between both "Opening" song blocks and their following **Markov transitions**
* Added function `generate_from_motif()` to fetch and map motif-level note data while applying chord validation/mapping logic
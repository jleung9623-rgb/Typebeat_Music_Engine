#### [7.2.1-alpha] - 2026-04-03

#### Added
- `main` folder created for core user-facing processes
- `engine` folder created for musical engine scripts
- `engine/data_initialization.py` for fetching track, blueprint, and metadata profiles
- `engine/markov_engine.py` script created for low-level composition state generation
- `engine/harmonic_analyzer.py` script created for motif transposition
- `engine/midi_builder.py` script created for constructing final MIDI file
- `main/main.py` script created for final user-facing song generation process
- `engine/aliases.py` created for decoupled asymmetric input validation
- Updated **ADR** entries #15-26
- `docs/ROADMAP.md` for potential future implementations

#### Changed
- Moved `upload_interface` into `main` folder
- Move `midi_extractor.py` into `scripts` folder
- Renamed `scripts` to `data-inflow`

#### Removed
- `UserPreference` class removed from `models.py`
- Old `engine.py` script removed
- Old `typebeat-v7.1` script removed
- `test_20260306_193443.mid` file removed


#### [7.2.0-alpha] - 2026-03-14

#### Added
- `SQLAlchemy` ORM integration for all related tables.
- `Alembic` migration environment for version-controlled schema changes.
- `migrations` folder with an `env.py` script that configures Alembic environment
- `versions` folder for Alembic save states
- Folders for `scripts` (Core program files) and `database` (SQL Initialization and database models)
- Added `__init__.py` initialization file for both folders
- CSV Upload and static music data seeding scripts (`harmonic_map.py`, `metadata_sb_upload.py`, `motifs_upload.py`).
- User interface for upload selection and routing (`upload_interface`).
- Note musical and temporal data pipeline using `midi_extractor.py`script
- `docs` folder with new **Architectural Decision Record** (ADR)
- `data` folder for test data pertaining to each `upload_interface` option
- Updated **ADR** entries #1-14

#### Changed
- SQL database connection initialization now isolated and deferred to `connection.py`
- Refactored database schema into `models.py` to use SQLAlchemy Declarative Base.
- Migration from raw SQL initialization to using `alembic upgrade head` command.
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
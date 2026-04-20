#### [7.2.3-alpha] - 2026-04-20

#### Added
- New file `data/sample_data_inflow/mock_motif_upload.py` for testing motif upload pipeline
- New file `requirements-dev.txt` file for dev-side unit testing
- Added `Pytest` integration for basic unit testing
- New file `data_inflow/transitions_upload.py` for mapping transitions as a supplement to `data_inflow/motifs_upload.py`
- Added `motif_tag` column to the `Motif` table under `database/models.py` for higher-order stochastic logic and grouping for `data_inflow/transitions_upload.py`
- Implemented logic within `engine/harmonic_analyzer.py` calculating a final transposed pitch that is within the standard frequency range of synthesizers and MIDI readers
- Implemented logic initiating a temporary session within `main/upload_interface.py` to seed chord data for motif uploads
- Updated **ADR** entries #28-37

#### Changed
- Changed junction link print statement guardrails in uploader scripts to `Raise ValueError` statements
- Fixed missing junction link logic for `track_motif_map` table within `engine/harmonic_analyzer.py`
- Fixed missing upload requirements for track-level scale data and missing junction link for `track_scale_map`
- Fixed relationship between applying track-level and motif-level transposition logic in `engine/harmonic_analyzer.py`
- Fixed transition logic within `engine/markov_engine.py` to select the next motif based on the Song Blueprint property `block_position`
- Renamed CSVUploader elements within uploader functions to be more distinct
- Fixed logic in `main/main.py` to include `phrase_latency` and `motif_pivot_offset` within the MIDI output generation
- Fixed logic in `engine/data_initialization.py` to sanitize scale interval strings during the fetching process

#### [7.2.2-alpha] - 2026-04-12

#### Added
- Unique constraint added to `MotifStat` column `motif_id` in `models.py`
- `data_inflow/transitions_upload.py` for mapping motif transitions
- `data/sample_data_inflow/mock_motif_upload.py` for mass-uploading "junk" motifs ahead of testing
- Introduced `motif_tag` string column to the `Motif` table in `models.py`
- Mandatory session rollbacks for junction table mapping in `motifs_upload.py` and `metadata_sb_upload.py`
- Dedicated `build_chord_cache` method and initialization check within `upload_interface.py`
- Updated **ADR** entries #27-32

#### Changed
- Fixed `harmonic_analyzer.py` and `markov_engine.py` logic to include motif-level **phrase latency** and **pivot offset** values
- Fixed Track-level Transposition logic in `harmonic_analyzer.py`
- Transitioned to a unified batch uploader in `motifs_upload.py`
- Renamed `CSVUploader` classes in `motifs_upload.py` and `metadata_sb_upload.py`
- Fixed SectionClass verification logic in `markov_engine.py`
- Moved `session.close()` calls in orchestrator scripts to primary execution scope

#### Removed
- Replaced `print()` statements with hard aborts for junction mapping instances in `motifs_upload.py` and `metadata_sb_upload.py`
- Removed isolated motif upload function in `motifs_upload.py`

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
- Renamed `scripts` to `data_inflow`

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
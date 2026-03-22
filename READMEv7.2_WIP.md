# Typebeat Musical Governance AI V7.2 WIP (Re-Factor for a Module-Based Program) --- Last Updated on 03/19/2026

## **Quick Start**
### Install Dependencies
The engine requires **Python 3.8+** and a **MySQL** server. 

1. **Create and Activate Virtual Environment**
```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
```

2. **Install Core Dependencies**
```bash
    pip install -r requirements.txt
```

3. **Configure Environemnt**
```text
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_NAME=typebeat_ai
```

4. **Deploy SQL Schema**
```bash
    alembic upgrade head
```

5. **Seed the Harmonic Library**
```bash
    python scripts/harmonic_map.py
```

6. **Ingest Metadata & Blueprints**
```bash
    python scripts/metadata_sb_upload.py
```

7. **Upload Dynamic Motifs**
```bash
    python scripts/motifs_upload.py
```

8. **Optional: Unified Upload Interface**
```bash
    python upload_interface.py
```

### Key Features

* **Dynamic Music Engine**: Uses Music21 to generate note sequences from multiple instruments as MIDI objects.
* **Sanitized Filenames**: Automatically filters illegal characters and timestamped to prevent overwrites.
* **Protocol-Compliant Routing**: Implements a Guardrail for the **Percussion Channel (10)** to ensure newly appended instruments do not conflict with the dedicated 'Drums/Percussion' MIDI channel.
* **SQL Server Integration**: Environment-driven access to a **MySQL** database that utilizes a .env configuration for database access across different local or server environments.

### Core Technologies

#### Database Driver & Environment
* **mysql-connector-python>=8.0.0**: Establishes the relationship between SQL and Python
* **python-dotenv>=1.0.0**: Allows use of .env files for secure access credentials

#### ORM & Database Schema Migration
* **SQLAlchemy>=2.0.0**: Translates database queries and connections into *Pythonic* properties
* **alembic>=1.10.0**: Streamlines database version control and deployment

#### Music Processing
* **music21>=9.1.0**: Translates musical theory and data into tangible objects and scores
* **mido>=1.2.10**: Low-level MIDI parsing for note extractor

#### Data Manipulation
* **pandas>=2.0.0**: CSV batch processing and validation

### Description

The Typebeat Musical Governance AI is a hierarchical, symbolic musical engine designed to generate musically coherent MIDI sequences across diverse genres using **Stochastic Logic** and state-based navigation. With the "proof of concept" now completed and validated, the Version 7.2 Model will now be undergoing a large-scale refactor of the engine itself to replicate a more **Professional-Grade Program**. The first major change in Version 7.2 is the continuation towards a **Modular System**, rather than a close-knit coupling of "monolithic" scripts. The previous `DatabaseManager` class has now been split into a `connection.py` script representing the connection to the SQL database, and a `models.py` script that uses SQLAlchemy to initialize each of the database's tables and relationships in a manner Python can read without copying queries word-for-word. The **Typebeat SQL Database** has also been targeted as the foundation, where the rest of the program will be rebuilt from the ground up. The newly refactored SQL database has now implemented a multitude of **Many-to-Many** relationships through the addition of junction tables. The database upload functionality has also been heavily expanded upon, now integrating a dynamic `upload_interface` that connects with multiple upload and seeding modules whose purposes have been divided based on the database's core faculties. Furthermore, an offline data pipeline has been established for motifs and motif notes in particular, where a MIDI ingestor script now extracts the necessary temporal and musical note data before compiling the information in a database-readable CSV format, where it is now eligible for upload. The previous `engine.py` and `typebeat-v7.1.py` main script will be rebuilt as a modular package, with some of the remaining distribution of responsibilities being segmented among *Chord Detection*, *Markov Training*, *Transposition*, *Track Selection*, *User Preferences*, and *Blueprint Logic*.

The Version 7.1 model evolves into a top-down structural engine by switching to **Song Blueprints** and recontextualizing notes, chords, and motifs as **Harmonic Events**, allowing for macro-level composition constraints. It is designed to condition other **Neuro-symbolic AI** or **Neural Networks** by filtering their learning material through a rigid framework of **Musical Laws**, providing a mathematically sound frame of reference for defining song structure. Using a newly **modularized** Python architecture and a **relational MySQL database** as the basis for its "logical supply", the program acts as an exponentially scalable platform for **Music Information Retrieval (MIR)**. Typebeat V7.1 ensures all generated content undergoes a "Quality Control Audit," primed by a customizable matrix of genre-specific regulations while strictly adhering to **MIDI 1.0 hardware protocols** and **General MIDI (GM) Standards**.

### Design Decisions

* **SQLAlchemy Database Classes**: The external module `SQLAlchemy` is now being used to create a **Comprehensive Database Matrix**, called `models.py`. This file acts as a Pythonic representation (Pseudo-schema) of the Typebeat SQL database, its table data and relational links, that also serves as a complement to the migration-focused `alembic` library, that helps with initializing a Python-focused version control route regarding the database.

* **Alembic Database Migration**: This library is also now being utilized to track changes to the database structure. `alembic` also gives a certain degree of agency for the user to automate structural modifications (Adding/Removing/Renaming tables and columns) to the database, by synchronizing the MySQL server with the SQLAlchemy Metadata defined in `models.py`. This tool ensures congruency between the Python application state and the live database environment.

* **SQL Database Refactor Phase II**: Multiple junction tables have now been added to `models.py` to establish a **Many-to-Many** relationship between tables that required interchangeable data (e.g. Multiple genres needing to be available for multiple artists, multiple genres and blueprints, etc.).

* **SQL Database Faculty Distribution**: The core aspects of the SQL database have now been clearly defined as 4 specific groups. These are the **Static Library (Chords & Scales)**, **Dynamic Library (Motifs & Motif Notes)**, **Metadata (Artists)**, and **Macro-Level Constraints (Genres, Tracks, Song Blueprints)**. The corresponding modules also follow the 4 faculties. However, Metadata shares the same parent program as the Macro-Level constraints, due to the relationship between the `Artist` and `Genre` classes in `models.py`, now represented by a junction table.

* **Modular Distribution**: The CSV uploader (Previously constructed using `pandas` as the primary driver) has now been expanded to a variety of upload and seeding modules, to not only address the notion that different faculties require different types of uploads (e.g. The static library must be validated as keys and mathematical integer note values before being added to the database, while the dynamic library must be validated as multiple types of data like temporal float values and note-level integers need to be collected into the same output container). The Static Library data can be appended to the database using the seeding program, while a CSV upload is required for the faculties that require multiple types of data. This enhanced modular structure for uploading data specifically also benefits a "plug and play" philosophy for potential future implementations, where features like as JSONB data compression and .WAV file analyzers now only require the development of a new script, rather than another full-scale remodel of a monolithic master program.

* **MIDI Extractor Data Pipeline**: Using `mido` as the


* **SQL Database Refactor**: The `transitions` table no longer holds note-level musical data, as the new table `motif_notes` has been created to integrate the `chords` table into each motif, in addition to adding **Markov selection logic** for both initial motif selection and next motif selection using two different weightings (At a motif, and transition level). This enhanced process of motif selection is further substantiated by the addition of the `song_blueprints` table, which serves as an ordered list of motif "containers" that are classified based on traditional song structure terms (Chorus, Verse, Bridge, etc.). This database is currently in the phase of a minimum viable product, and will undergo additional phases of refactoring as higher-level logic and user-facing features get added.
* **Back-End CSV Upload Integration**: Though the user-facing ability to actually upload a CSV file to the database has yet to be added, the core logic behind the feature is implemented, using the `pandas` library as the main catalyst. An additional helper function is run prior to the upload itself that designates a set of essential columns that the user must include in their CSV file as they upload, else the program will return an error. The final purpose of adding this feature is to mass import data into multiple tables, where different types of upload (Metadata, blueprints, musical data) will constitute different sets of essential columns. The CSV uploads are dynamic, so column order in the processed file does not matter during the transfer of data. This current CSV upload function is latent in the program, and has reached the "proof of concept" stage, but has yet to be optimized for my database.
* **Song Structure Implementation**: A new table, called `song_blueprints` was added to serve as a hierarchical constraint for the song itself. The elements of this table serve as **top-level containers**, where a "Song Block" is designated based on the current musical stanza, and then houses any number of motifs based on the blueprint's timeline until the full runtime is reached. The hierarchy then becomes *Song Block > Motif > Motif Notes* for each container in a blueprint's sequence.
* **Motif-Level Musical Data**: To support the integration of song blueprints, motifs and individual notes were now consolidated into pure **Harmonic Events**. `transitions` are now conducted strictly at a harmonic event level, with the `motifs` table encapsulating any individual note, chord, or harmonic phrase involving both, acting as a "Hub" for all musical data applicable to each event.
* **Harmonic Normalization**: To prevent the engine from generating mathematically "correct" but musically dissonant keys, baseline harmonic data (such as the `default_root_note`) was migrated out of the genres table and strictly bound to the scales table. This allows the Python engine to mathematically calculate the transposition between a motif's original key and the target song's scale without relying on ambiguous pitch values.

### **Edge Case Mitigation (General)**

* **Save File I/O Protection**: Implemented a guardrail to differentiate between **writing errors** (Permission issues, insufficient disk space, invalid filenames) and other unexpected **system errors** during the MIDI export phase.
* **Input Sanitization**: Implemented **Regex-based filtering** and unique **timestamping** for all file exports to prevent OS-level filename errors and data overwrites.

### **Edge Case Mitigation (database.py)**

* **MySQL Database Connection Failure**: Implemented **Graceful Failure** for SQL connection errors, where the system audits a user's credentials via a .env check and provides a clear notification before a clean exit in error cases, preventing unhandled traceback crashes.
* **Fetch Function Memory Isolation**: Used context managers **(with statements)** inside **try/except** blocks within every function that "fetches" information from the SQL database to automatically free the allocated memory at the end of each function regardless of outcome.
* **User Upload Processing Protection**: **Default values** were set for non-required fields pertaining to harmonic events in the case no data was uploaded into them. The function also explicitly returns error messages for missing required columns, and strictly **rejects uploads** containing **Forbidden Columns** to prevent database contamination.
* **CSV Upload Data Inflow**: Added **Commit** protection against race conditions during bulk uploads to SQL database. Upload errors trigger a **Rollback** to revert the database to its prior state, intentionally leaving incremental ID gaps as an implicit audit trail.

### **Edge Case Mitigation (Music Engine)**

* **Hardware Conflict Resolution**: Melodic instruments assigned to the hardware-reserved **Percussion Channel (10)** are automatically re-routed using a **Modulo Fallback** logic to prevent auditory corruption.
* **Protocol Enforcement**: Monitored active MIDI tracks to ensure the system never exceeds the **16-channel hardware limit**, providing user notifications for channel overlaps.
* **Key-Error Normalization**: Utilized **lowercase string normalization** for internal dictionary lookups while preserving "Pretty Case" metadata for the final MIDI display.
* **User Preference Fallback Settings**: Applied a "Contingent default" fallback setting for keys missing from the `user_preferences` table in the SQL database (e.g. setting a default BPM of 120, or a default composition title of 'Typebeat AI V7 Generated Score' using the `.get('key', default)` dictionary method).
* **Stochastic Dead-End Protection**: If a motif's **Markov Chain** reaches a dead end (no valid outward transitions for the required Song Block), the engine safely breaks the chain and initiates a **Global Pool Fallback**, fetching a contextually valid motif from the database without crashing the generation loop.

### SQL Database Architecture
The engine is powered by a relational MySQL schema optimized for **stochastic memory persistence**.

* **Visual Schema**: [View Interactive ERD on dbdiagram.io](https://dbdiagram.io/d/Typebeat-7-0-69a48308a3f0aa31e172e557)

* **`genres`**: The defining registry of "Song Archetypes" containing default tempo, root notes, and scale associations.
* **`tracks`**: Hardware routing table mapping MIDI instruments and patch numbers to specific genres.
* **`transitions`**: The stochastic network that stores Markov state weights and rhythmic profiles.
* **`scales` / `chords` / `chord_notes`**: The musical foundation providing interval and harmonic structures.
* **`artists` / `motifs`**: High-level curated sequences and artist-specific style profiles.
* **`compositions`**: Table for generated scores, file paths, and session metadata.
* **`user_preferences`**: EAV-pattern table for session-persistent global configurations.
* **`motif_notes` (NEW)**: Contains data for each note in a motif sequence. Converts notes, chords, and mixed musical sequences into **Harmonic Events**
* **`song_blueprints` (NEW)**: Determines structure of song through **Song Blocks** (e.g. "Intro > Verse > Build > Chorus > Rest > etc.")

#### **Future Roadmap** 

* Add protocol for unit testing
* Begin populating database to accommodate motif variations
* Expand routing registry for tracks table (To expand library of instruments, perhaps routing through a DAW)
* API integration for DAWs (Ableton, etc.)
* Add note velocity designation into 'transitions', 'motifs', 'chord_notes'
* Add Spatial Imaging to the Hardware Registry
* Heavier encryption ahead of a public-facing model
* Integrate 'AuthN' and 'AuthZ' into program
* Import NumPy, PyTorch libraries for neuro-symbolic transition
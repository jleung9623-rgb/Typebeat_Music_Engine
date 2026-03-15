# Typebeat Musical Governance AI V7.1 (A Symbolic Quality Control System) --- Completed on 03/09/2026

## **Quick Start**
### Install Dependencies
The engine requires **Python 3.8+** and a **MySQL** server. 

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd typebeat-ai-v7
   ```
2. **Install Core Libraries:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Create and Activate Virtual Environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Configure Environment:**
    Create a .env file in the root directory:
    ```text
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_NAME=typebeat_ai_v7
    ```
5. **Run Engine:**
    Ensure the Master Schema is imported into MySQL before execution.
    ```python typebeat-v7.py```

### Key Features

* **Dynamic Music Engine**: Uses Music21 to generate note sequences from multiple instruments as MIDI objects.
* **Sanitized Filenames**: Automatically filters illegal characters and timestamped to prevent overwrites.
* **Protocol-Compliant Routing**: Implements a Guardrail for the **Percussion Channel (10)** to ensure newly appended instruments do not conflict with the dedicated 'Drums/Percussion' MIDI channel.
* **SQL Server Integration**: Environment-driven access to a **MySQL** database that utilizes a .env configuration for database access across different local or server environments.

### Core Technologies

* **Music21**: Specialized toolkit for computer-aided musicology and MIDI object manipulation.
* **MySQL Connector**: High-performance driver for relational music data and Markov state persistence.
* **Python-Dotenv**: Manages environment-based configuration for modular database access.

### Description

The Typebeat Musical Governance AI is a hierarchical, symbolic musical engine designed to generate musically coherent MIDI sequences across diverse genres using **Stochastic Logic** and state-based navigation. The Version 7.1 model evolves into a top-down structural engine by switching to **Song Blueprints** and recontextualizing notes, chords, and motifs as **Harmonic Events**, allowing for macro-level composition constraints. It is designed to condition other **Neuro-symbolic AI** or **Neural Networks** by filtering their learning material through a rigid framework of **Musical Laws**, providing a mathematically sound frame of reference for defining song structure. Using a newly **modularized** Python architecture and a **relational MySQL database** as the basis for its "logical supply", the program acts as an exponentially scalable platform for **Music Information Retrieval (MIR)**. Typebeat V7.1 ensures all generated content undergoes a "Quality Control Audit," primed by a customizable matrix of genre-specific regulations while strictly adhering to **MIDI 1.0 hardware protocols** and **General MIDI (GM) Standards**.

### Design Decisions

* **Program Code Split**: To ensure organizational integrity, the architecture was modularized. The main execution flow was separated from the Musical Engine (`engine.py`), which now strictly handles the generation and mapping of MIDI objects. Simultaneously, the database interaction was isolated into its own module (`database.py`) to manage the secure "handshake" of data flowing between Python and SQL.
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
# Typebeat Musical Governance AI V7.2.1 (Re-Factor for a Module-Based Professional Program) --- Last Updated on 04/03/2026

## **Quick Start**

### Install Dependencies
The engine requires **Python 3.10+** (for union type hinting support) and a **MySQL** server. 

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

3. **Configure Environment**: Create a .env file in the root directory.
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

7. **Optional: Convert MIDI Files Into CSV Format**
```bash
    python scripts/midi_extractor.py
```

8. **Upload Dynamic Motifs**
```bash
    python scripts/motifs_upload.py
```

9. **Optional: Access Unified Upload Interface**
```bash
    python main/upload_interface.py
```

10. **Access The Typebeat Program**
```bash
    python main/main.py
```

### Key Features

* **Stochastic MIDI Generation**: Uses a polyphonic `Markov Engine` that generates musically coherent timelines based on trained motif transitions. Leverages **Mido** to generate a composition timeline that accommodates human timing through motif phrase latency.

* **Asymmetric Input Validation**: Employs parallel logic gates for `user input overrides`, ensuring that inputs are consistent with SQL database information by process of input aliases

* **Sanitized Filename Saving**: Automatically filters illegal characters using `Regex` to prevent overwrites and ineligible composition titles.

* **Payload Construction Pipeline**: Utilizes specialized workers in the `engine` folder to construct a sealed output payload for the MIDI file generation, prioritizing Command-line-injected overrides over database fallback values.

* **Pythonic SQL Server Integration**: Environment-driven access to a **MySQL** database that utilizes a .env configuration for database access across different local or server environments. Integrates **SQLAlchemy** as a means to utilize Object-Oriented Mapping while also keeping a "master schema" of sorts for the database as a Python-interactible file. Also uses **Alembic** for migration control, command-line database updates and schema edit logging.

* **Many-to-Many Schema Architecture**: Orchestrates complex relationships between `Artists`, `Genres`, `Tracks`, `Motifs`, and `Scales` via optimized `junction tables` for maximum query flexibility.

* **Static & Dynamic Database Uploading**: Adopts a `modular approach` to data inflow, with `seeding programs` being used for sending static harmonic translation requirements into the database and `CSV upload programs` (Through **Pandas**) being used for dynamic data such as motif information, macro-level song constraints, and overarching metadata.

* **Dedicated Motif Data Pipeline**: Establishes an offline path for motif data inflow by allowing the user to parse MIDI files as an input through `midi_extractor.py` to break the note data down into a digestible format that the database would accept.

### Core Technologies

#### Database & Environment
* **mysql-connector-python>=8.0.0**: The core driver establishing the physical connection between SQLAlchemy and the MySQL server.
* **SQLAlchemy>=2.0.0**: Handles ORM mapping and Many-to-Many relationship resolution.
* **Alembic>=1.10.0**: Manages version-controlled schema migrations.
* **python-dotenv>=1.0.0**: Allows use of .env files for secure access credentials

#### Music Processing
* **mido>=1.2.10**: Low-level MIDI parsing for note extractor

#### Data Manipulation
* **pandas>=2.0.0**: CSV batch processing and validation

### Description

The Typebeat Musical Governance AI is a symbolic musical engine designed to generate musically coherent MIDI sequences across diverse genres using Stochastic Logic and state-based navigation.

Version 7.2.1 represents a complete transition from a monolithic "proof of concept" to a Professional-Grade Modular Architecture. The system is built on a foundation of strict Separation of Concerns:

1. **The Orchestrator (main.py)**: A stateless router that normalizes user intent and validates data against the alias library.

2. **The Configuration Layer (aliases.py)**: A quarantined module for all deterministic string-to-integer mappings in the main execution loop, preventing static data bloat in the execution logic.

3. **The Construction Layer (engine)**: A multi-worker system that resolves the delta between user requests and database records to build a finalized execution profile.

4. **The Markov Engine & Analyzer (engine)**: Independent modules that execute the generation and transposition logic. These modules are currently implemented with a Linear $O(n)$ Database Complexity (N+1 Query Pattern) to provide a performance baseline for future optimizations. This modular refactor ensures the engine remains extensible, allowing for future implementations of eager-loading caches or micro-timing groove limits without requiring a rewrite of the core SQL schema.

5. **The Data Inflow Engine (data-inflow)**: A comprehensive sub-set of program files that serve to upload both static and dynamic types of data directly to the SQL server. Core processes are segmented based on the specific faculties of the Typebeat Engine they address and the nature of their in-database table relationships within the data network.

6. **SQL Database Architecture**: The Typebeat program's foundation lies in a relational MySQL database optimized for **stochastic memory persistence**.

* **Visual Schema**: [View Interactive ERD on dbdiagram.io](https://dbdiagram.io/d/Typebeat-v7-2-Final-69d010d38089629684170028)
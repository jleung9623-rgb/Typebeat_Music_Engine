# Architectural Decision Record 0006 - Modular Architecture Distribution

## Tags: #SYS-ARCH, #CODE-ORG
## Status: Accepted

### Context
Housing database connections, ORM models, and data ingestion logic in monolithic scripts caused circular import failures and redundant memory allocation when the UI was initialized.

### Decision
Decouple the architecture into strict domain-specific directories:
* `/database`: Exclusively for `models.py` and `connection.py`.
* `/scripts`: Exclusively for isolated ingestion logic (`motifs_upload.py`, `metadata_sb_upload.py`).
* UI interfaces (`upload_interface.py`) act strictly as transaction managers and must import dependencies at the top level.

### Consequences
* **Constraint**: Ingestion scripts cannot define their own database engines; they must import `SessionLocal` from the `/database` directory.
# Architectural Decision Record 0029 - Data Inflow Fault-Tolerance Protocol

## Module: motifs_upload.py, metadata_sb_upload.py
## Tags: #FAULT-TOLERANCE, #SESSION-MANAGEMENT, #DATA-INTEGRITY
## Status: Accepted

### Context
The `data_inflow` directory exhibited asymmetric error propagation. Core initialization failures caused fatal thread crashes, while relational junction mappings (e.g., mapping a track to a genre) failed silently, risking the creation of floating, orphaned database nodes.

### Decision
Established a strict "Fatal Pipeline" architecture across all ingestion modules.

* **Lifecycle Management**: Executed centralized session lifecycle management exclusively within the orchestrator scripts.

* **Hard Aborts**: All silent mapping failures were replaced with hard exception raises to guarantee immediate transaction termination.

### Consequences
* **Requirement**: A single misaligned row or mapping failure specifically for junction mapping instances instantly triggers a `session.rollback() `and aborts the entire batch upload, demanding strict pre-validation of ingestion files.

* **Stability**: Total database state integrity is mathematically guaranteed.
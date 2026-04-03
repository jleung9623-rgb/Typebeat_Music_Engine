# Architectural Decision Record 0012 - UI Ingestor API Contract

## Module: upload_interface.py
## Tags: #API-CON
## Status: Accepted

### Context
The `upload_interface` was failing to accurately report internal ingestion errors. Because ingestors were catching their own exceptions to preserve batch integrity, the UI was incorrectly reporting `SUCCESS` even when the switchboard returned a validation error.

### Decision
Standardize the communication between all UI elements and Ingestor scripts via a rigid dictionary contract:

* **Implemented Code Format**: `return {"status": "success" | "error", "message": str(e)}`

### Consequences
* **Requirement**: The UI must explicitly evaluate if result['status'] == 'success': before committing a transaction or printing a success message.

* **Constraint**: Returning raw strings or raising unhandled exceptions for expected validation failures is forbidden.
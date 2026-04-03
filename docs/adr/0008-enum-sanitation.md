# Architectural Decision Record 0008 - Enum Consolidation Sanitation

## Module: upload_interface.py
## Tags: #SAN-IN, #DB-INT
## Status: Accepted

### Context
The system utilized diverging Enums (`BlockClass` vs `MotifClass`), leading to KeyError crashes in the `upload_interface`. Furthermore, user inputs containing hyphens or spaces (e.g., "Pre-Chorus") failed to map to Enum keys (e.g., `PRE_CHORUS`).

### Decision
Consolidate all structural musical containers into a single SectionClass Enum within models.py. Implement a universal string sanitizer in all UI and Ingestor layers:

* **Implemented Code**: `valid_str = input_str.upper().replace("-", "_").replace(" ", "_")`

### Consequences
* **Requirement**: All future modules must import `SectionClass`.

* **Constraint**: Manual string-to-Enum mapping without the chained `.replace()` sanitizer is a violation of technical discipline.
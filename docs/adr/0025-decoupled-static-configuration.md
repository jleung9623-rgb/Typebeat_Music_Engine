# Architectural Decision Record 0026 - Asymmetric Input Validation for Modulatory Variables

## Module: aliases.py
## Tags: #SYS-ARCH, #MODULARITY, #STATE-MGMT
## Status: Accepted

### Context
The orchestrator (`main.py`) required static mapping dictionaries to translate imprecise human string inputs into mathematically rigid database constraints (`SCALE_ALIASES`) and pure MIDI integers (`ROOT_ALIASES`). Hardcoding these dictionaries directly into the primary execution loop violated the Single Responsibility Principle. It bloated the orchestrator with non-operational static data, merged configuration state with execution state, and introduced a severe maintenance bottleneck as the engine inevitably scales to accommodate additional genre, chord, or blueprint aliases.

### Decision
Extract and quarantine all deterministic routing dictionaries into a dedicated static configuration module (`aliases.py`).

* The orchestrator imports this file strictly as a read-only translation layer during the payload hydration phase.
* Execution logic and database fallback logic remain entirely structurally agnostic to the contents or size of the configuration dictionaries.

### Consequences
* **Requirement**: Any future additions to the static schema (e.g., introducing non-Western microtonal scales or alternate tuning root notes) mandate a manual update to `aliases.py` completely independent of SQL schema migrations.

* **Stability**: The orchestrator is mathematically sealed against configuration bloat. The execution pipeline's complexity remains constant regardless of how massive the human-to-machine alias dictionary becomes.
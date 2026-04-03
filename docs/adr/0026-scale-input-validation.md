# Architectural Decision Record 0026 - Asymmetric Input Validation for Modulatory Variables

## Module: main.py
## Tags: #INPUT-VALIDATION, #DATA-INT, #HARMONICS
## Status: Accepted

### Context
The orchestrator prompts users for two optional *harmonic overrides*: Scale Name and Root Note. Initially, these evaluations were structurally nested, causing the rejection of a scale override to inadvertently nullify a valid root note override. Furthermore, attempting to apply uniform else error handling to both inputs ignored the fundamental differences in their downstream architectural dependencies. The SQL initialization worker is designed to gracefully handle invalid scale strings via random fallbacks, whereas the harmonic transposer is strictly mathematical and will fatally crash if fed an invalid root note string instead of an integer.

### Decision
Decouple the variable captures into strictly parallel conditional blocks and implement asymmetric validation logic based on downstream requirements.

* **Independent Evaluation**: `scale_input` and `root_input` are evaluated as parallel, independent boolean gates to ensure optional variables do not nullify each other when skipped (pressing Enter).
* **Graceful Delegation (Scale Input)**: Pass all non-empty strings (valid or invalid) through the `SCALE_ALIASES` dictionary and directly into the payload. Error handling is intentionally omitted at the CLI level, delegating the resolution of invalid strings to the SQL worker's pre-established random.choice() fallback mechanisms.
* **Strict Gatekeeping (Root Input)**: Evaluate non-empty strings strictly against the `ROOT_ALIASES` dictionary. If validation fails (the string cannot be mapped to a MIDI integer), the orchestrator intercepts the failure, throws a CLI error, and refuses to attach the invalid data to the payload, reverting to the SQL schema's default.

### Consequences
* **Requirement**: The `harmonic_analyzer.py` engine relies entirely on `main.py` to sanitize its input parameters; it must never be exposed to raw string evaluation.

* **Stability**: The orchestrator correctly balances graceful database fallbacks with strict mathematical type safety, mathematically preventing runtime crashes in the transposer while avoiding hostile user experience loops.
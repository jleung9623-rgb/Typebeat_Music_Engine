from data_inflow.procedural_engine.core_generator import ProceduralOrchestrator
from data_inflow.procedural_engine.harmony_domain.trap_voicings import TrapVoicing

# Use the command ".\venv\Scripts\Activate.ps1" to activate a virtual environment beforehand

def test_trap_voicing_pipeline():
    """
    Verifies that the ProceduralOrchestrator correctly routes a raw matrix
    through the TrapVoicing module and enforces the mathematical pitch constraints.
    """
    # Instantiates the architecture and state
    orchestrator = ProceduralOrchestrator()
    trap_module = TrapVoicing(priority_weight=90) # Register the Romain Module (Weight 90)
    orchestrator.register_module(trap_module)

    raw_matrix = [
        {"pitch_value": 40, "beat_position": 1.0, "duration": 1.0, "micro_offset": 0.0, "velocity": 100},
        {"pitch_value": 62, "beat_position": 2.0, "duration": 0.5, "micro_offset": 0.0, "velocity": 100},
        {"pitch_value": 55, "beat_position": 3.0, "duration": 1.0, "micro_offset": 0.0, "velocity": 100}
    ]

    # Transfers the data through the core generator
    mutated_matrix, final_tag = orchestrator.generate_motif(raw_matrix)
    
    # Assertions: Validates exact mathematical expectations
    assert final_tag == "TRAP_VOICING", f"Expected tag 'TRAP_VOICING', got '{final_tag}'"
    assert len(mutated_matrix) == 3, "Matrix length was mutated. Polyphony corrupted."

    # Rule 1: Bass note (E2 / 40) -> Should be compressed to Root (C2 / 36)
    assert mutated_matrix[0]["pitch_value"] == 36, "Failed to compress Bass Major 3rd to Root."

    # Rule 2: Upper note (D4 / 62) -> Should be compressed to Minor 2nd (Db4 / 61)
    assert mutated_matrix[1]["pitch_value"] == 61, "Failed to compress Upper Major 2nd to Minor 2nd."

    # Rule 3: Safe note (G3 / 55) -> Must remain untouched
    assert mutated_matrix[2]["pitch_value"] == 55, "Safe pitch value was illegally mutated."
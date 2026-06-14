from database.connection import SessionLocal
from database.models import SectionClass

from data_inflow.procedural_engine.core_generator import ProceduralOrchestrator
from data_inflow.procedural_engine.procedural_exporter import ProceduralExporter

# STRICT CORRECTION: Complete domain module imports
from data_inflow.procedural_engine.harmony_domain.modal_interchange import ModalInterchange
from data_inflow.procedural_engine.harmony_domain.trap_voicings import TrapVoicing
from data_inflow.procedural_engine.rhythmic_domain.quantized_grid import QuantizedGrid
from data_inflow.procedural_engine.melodic_domain.passing_tones import PassingTones
from data_inflow.procedural_engine.articulation_domain.dilla_swing import DillaSwing
from data_inflow.procedural_engine.velocity_domain.velocity_humanizer import VelocityHumanizer

def execute_mass_generation(batch_size: int, track_id: int, markov_progression: list[str], target_class: SectionClass):
    """
    Spins up the Procedural Generator, runs X iterations, and exports the CSVs.
    """
    session = SessionLocal()
    orchestrator = ProceduralOrchestrator()
    exporter = ProceduralExporter()
    
    print("\n--- BOOTING NEUROSYMBOLIC FORGE ---")
    
    # 1. Register Active Domains (Enforce chronological execution)
    orchestrator.register_module(ModalInterchange())
    orchestrator.register_module(TrapVoicing())
    orchestrator.register_module(QuantizedGrid())
    orchestrator.register_module(PassingTones())
    orchestrator.register_module(DillaSwing())
    orchestrator.register_module(VelocityHumanizer())

    print(f"Executing {batch_size} synthetic iterations for Track ID {track_id}...")

    try:
        for i in range(1, batch_size + 1):
            # Define unique synthetic batch name
            base_filename = f"SYNC_GEN_T{track_id}_{target_class.name}_{i}"
            
            # Execute the Generation Pipeline
            motif_matrix, applied_tags = orchestrator.generate_motif(
                session=session,
                track_id=track_id,
                markov_progression=markov_progression
            )
            
            # Export Matrix to strictly formatted CSV
            output_path = exporter.export_motif_to_csv(
                motif_matrix=motif_matrix,
                base_filename=base_filename,
                motif_class=target_class
            )
            
            print(f"[{i}/{batch_size}] Exported: {output_path} | Tags: {applied_tags}")
            
    except Exception as e:
        print(f"CRITICAL FAILURE during batch generation: {str(e)}")
    finally:
        session.close()
        print("--- FORGE OFFLINE ---")

if __name__ == "__main__":
    # Example test parameters. 
    # You will eventually pull these dynamically or via sys.argv
    test_track_id = 1 
    test_progression = ["C_MIN", "F_MIN", "G_DOM", "C_MIN"]
    test_class = SectionClass.VERSE
    
    execute_mass_generation(
        batch_size=5, 
        track_id=test_track_id, 
        markov_progression=test_progression, 
        target_class=test_class
    )
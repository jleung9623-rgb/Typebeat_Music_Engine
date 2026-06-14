from typing import List, Tuple, Dict, Optional
from enum import Enum
from sqlalchemy.orm import Session

class DomainType(Enum):
    HARMONY = 1     # Highest absolute priority: Pitch defines the structure
    RHYTHMIC = 2    # MUST precede MELODIC to supply beat_position
    MELODIC = 3
    ARTICULATION = 4
    VELOCITY = 5    # Lowest absolute priority: Dynamics rely on existing notes

class BaseProceduralConcept:
    """
    Base state container for procedural generation logic.
    """
    def __init__(self, domain_type: DomainType, concept_tag: str, priority_weight: int = 1):
        self.domain_type = domain_type
        self.concept_tag = concept_tag
        self.priority_weight = priority_weight

class ProceduralOrchestrator:
    """
    Manages the generation pipeline by routing state through strict domain boundaries.
    """
    def __init__(self):
        self.active_modules = []

    def register_module(self, module: BaseProceduralConcept):
        """Appends an instantiated domain module to the generation queue."""
        self.active_modules.append(module)

    def generate_motif(self, session: Session, track_id: int, markov_progression: List[str], modal_indices: Optional[List[int]] = None) -> Tuple[List[Dict], str]:
        """
        Executes the procedural pipeline. 
        Routes through the Symbolic Layer before resolving the Pitch Layer.
        """
        if modal_indices is None:
            modal_indices = []
            
        applied_tags = []
        current_midi_state: List[List[int]] = []
        current_temporal_state: List[Dict] = []
        current_string_state = markov_progression

        # Isolate the registered Harmony modules
        harmony_modules = [m for m in self.active_modules if m.domain_type == DomainType.HARMONY]
        
        # Step 1: Harmony Domain (Symbolic & Pitch Processing)
        if harmony_modules:
            # 1. Execute Symbolic Mutations (Modal Interchange)
            modal_module = next((m for m in harmony_modules if m.concept_tag == "MODAL_INTERCHANGE"), None)
            if modal_module:
                current_string_state = modal_module.process_progression(session, current_string_state, modal_indices)
                applied_tags.append(modal_module.concept_tag)

            # 2. Execute Pitch Calculations (Trap Voicing & Voice Leading)
            trap_module = next((m for m in harmony_modules if m.concept_tag == "TRAP_VOICING"), None)
            if trap_module:
                current_midi_state = trap_module.process_progression(session, current_string_state)
                applied_tags.append(trap_module.concept_tag)
            else:
                raise RuntimeError("Pipeline Failure: TRAP_VOICING module is missing. Cannot resolve pitch structure.")
        else:
            raise RuntimeError("Pipeline Failure: No Harmony Domain modules registered.")
        
        # Step 2: Rhythmic Domain (Temporal Mapping)
        rhythmic_modules = [m for m in self.active_modules if m.domain_type == DomainType.RHYTHMIC]
        if rhythmic_modules:
            groove_module = next((m for m in rhythmic_modules if m.concept_tag == "QUANTIZED_GRID"), None)
            if groove_module:
                current_temporal_state = groove_module.apply_temporal_grid(current_midi_state, midi_channel=1)
                applied_tags.append(groove_module.concept_tag)
            else:
                raise RuntimeError("Pipeline Failure: QUANTIZED_GRID missing.")
        else:
            raise RuntimeError("Pipeline Failure: No Rhythmic Domain modules registered.")
        
        # Step 3: Melodic Domain (Monophonic Interpolation)
        melodic_modules = [m for m in self.active_modules if m.domain_type == DomainType.MELODIC]
        if melodic_modules:
            passing_module = next((m for m in melodic_modules if m.concept_tag == "PASSING_TONES"), None)
            if passing_module:
                current_temporal_state = passing_module.apply_melodic_path(session, track_id, current_temporal_state)
                applied_tags.append(passing_module.concept_tag)
        
        # Step 4: Articulation Domain (Micro-Timing Mutations)
        articulation_modules = [m for m in self.active_modules if m.domain_type == DomainType.ARTICULATION]
        
        # We assign the current dictionary state to a mutable target for potential processing
        final_temporal_state = current_temporal_state
        
        if articulation_modules:
            for art_module in articulation_modules:
                # The bridge: List[Dict] -> Mutated List[Dict]
                final_temporal_state = art_module.apply_articulation(final_temporal_state)
                applied_tags.append(art_module.concept_tag)

        # Step 5: Velocity Domain (Dynamic Humanization)
        velocity_modules = [m for m in self.active_modules if m.domain_type == DomainType.VELOCITY]
        
        if velocity_modules:
            for vel_module in velocity_modules:
                # The final mutation: Injects the 'velocity' key
                final_temporal_state = vel_module.apply_dynamics(final_temporal_state)
                applied_tags.append(vel_module.concept_tag)

        final_tag_string = "|".join(applied_tags)

        # STRICT CORRECTION: We return the flat List[Dict] containing the completed matrices
        return final_temporal_state, final_tag_string
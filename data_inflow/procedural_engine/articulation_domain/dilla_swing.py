from typing import List, Dict
import random
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType

class DillaSwing(BaseProceduralConcept):
    def __init__(self, swing_amount: float = 0.08, humanize_downbeats: bool = True):
        """
        Calculates non-quantized grid mutations based on Dilla timing conventions.
        swing_amount: The positive delay applied to off-beat subdivisions.
        """
        super().__init__(domain_type=DomainType.ARTICULATION, concept_tag="DILLA_SWING")
        
        # Clinically capped to the database limits proven by midi_extractor.py
        self.swing_amount = min(abs(swing_amount), 0.125)
        self.humanize_downbeats = humanize_downbeats

    def apply_articulation(self, temporal_matrix: List[Dict]) -> List[Dict]:
        """
        Ingests the rigid temporal dictionary array and mutates the micro_offset values.
        """
        if not temporal_matrix:
            return []

        mutated_matrix = []

        for note in temporal_matrix:
            mutated_note = note.copy()
            beat = mutated_note['beat_position']
            
            # Detects 16th-note subdivisions (e.g., x.25, x.75) vs structural anchors
            is_offbeat = (beat % 0.5) != 0.0 
            
            offset = 0.0
            
            # 1. Structural Swing: Delay the offbeats
            if is_offbeat:
                offset += self.swing_amount
                
            # 2. Unanchored Drift: Humanize all notes slightly
            if self.humanize_downbeats:
                # Random drift between -0.03 and +0.03 to simulate imperfect striking
                drift = random.uniform(-0.03, 0.03)
                offset += drift

            # 3. Absolute Constraint Enforcement
            # Clamps the final offset between -0.125 and +0.125 to prevent grid snapping violations
            final_offset = max(-0.125, min(0.125, offset))
            
            mutated_note['micro_offset'] = round(final_offset, 3)
            mutated_matrix.append(mutated_note)

        return mutated_matrix
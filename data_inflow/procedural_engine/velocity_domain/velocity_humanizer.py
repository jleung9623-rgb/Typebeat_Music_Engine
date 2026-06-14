from typing import List, Dict
import random
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType

class VelocityHumanizer(BaseProceduralConcept):
    def __init__(self, min_velocity_floor: int = 25):
        """
        Calculates dynamic velocity based on rhythmic hierarchy and frequency bracketing.
        min_velocity_floor: Hard constraint to prevent notes from falling below the
        midi_extractor.py deletion threshold (defaulting slightly above 20 for safety).
        """
        super().__init__(domain_type=DomainType.VELOCITY, concept_tag="DYNAMIC_VELOCITY")
        self.min_velocity = min_velocity_floor
    
    def calculate_rhythmic_base(self, beat_position: float) -> int:
        """Establishes the foundational volume based on structural metronome placement."""
        # 1. Downbeats (1.0, 2.0, 3.0, 4.0) -> Heaviest Accent
        if beat_position % 1.0 == 0.0:
            return 105
        # 2. Upbeats (x.5) -> Standard Hit
        elif beat_position % 0.5 == 0.0:
            return 85
        # 3. Subdivisions (x.25, x.75) -> Ghost Notes
        else:
            return 65
        
    def calculate_frequency_modifier(self, pitch_value: int) -> float:
        # Bass Register (< MIDI 45): Needs power to anchor the mix
        if pitch_value < 45:
            return 1.15
        # Mid Register (MIDI 45 - 72): Standard polyphonic body
        elif 45 <= pitch_value <= 72:
            return 1.0
        # High Register (> MIDI 72): Needs reduction to prevent piercing frequencies
        else:
            return 0.85
        
    def apply_dynamics(self, temporal_matrix: List[Dict]) -> List[Dict]:
        """
        Ingests the finalized flat dictionary array and injects the 'velocity' key.
        """
        if not temporal_matrix:
            return []
        
        dynamic_matrix = []

        for note in temporal_matrix:
            mutated_note = note.copy()

            base_velocity = self.calculate_rhythmic_base(mutated_note['beat_position'])
            frequency_modifier = self.calculate_frequency_modifier(mutated_note['pitch_value'])

            # Apply the multiplier and introduce a small randomization variable (±5)
            raw_velocity = (base_velocity * frequency_modifier) + random.randint(-5, 5)

            # Absolute Constraint Enforcement
            # Must not exceed hardware limit (127) or fall below extractor threshold (25)
            final_velocity = max(self.min_velocity, min(127, int(raw_velocity)))
            mutated_note['velocity'] = final_velocity
            dynamic_matrix.append(mutated_note)

        return dynamic_matrix

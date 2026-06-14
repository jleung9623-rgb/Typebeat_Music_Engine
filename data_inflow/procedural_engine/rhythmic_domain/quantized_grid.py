from typing import List, Dict
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType

class QuantizedGrid(BaseProceduralConcept):
    def __init__(self, chord_duration: float = 2.0):
        """
        Initializes the universal Rhythmic Domain baseline.
        chord_duration dictates the rigid chronological spacing (in beats)
        assigned to each polyphonic event.
        """
        super().__init__(domain_type=DomainType.RHYTHMIC, concept_tag="QUANTIZED_GRID")
        self.chord_duration = chord_duration
    
    def apply_temporal_grid(self, polyphonic_matrix: List[List[int]], midi_channel: int = 1) -> List[Dict]:
        """
        Ingests stateless pitch arrays and projects them onto a universal temporal grid.
        Output a flat List[Dict] strictly compliant with the MotifNote SQL schema.
        """
        if not polyphonic_matrix:
            return []
        
        temporal_state = []
        current_beat = 0.0

        for chord_array in polyphonic_matrix:
            for pitch in chord_array:
                note_event = {
                    "pitch_value": pitch,
                    "beat_position": current_beat,
                    "duration": self.chord_duration,
                    "micro_offset": 0.0,
                    "midi_channel": midi_channel  # Injecting the routing key
                }
                temporal_state.append(note_event)
            
            current_beat += self.chord_duration
        
        return temporal_state
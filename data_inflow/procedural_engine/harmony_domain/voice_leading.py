from typing import List
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType

class VoiceLeader(BaseProceduralConcept):
    def __init__(self):
        super().__init__(domain_type=DomainType.MELODIC, concept_tag="VOICE_LEADING")

    def calculate_distance(self, chord_a: List[int], chord_b: List[int]) -> int:
        """Calculates the raw vertical distance between two sorted pitch lists."""
        return sum(abs(b - a) for a, b in zip(sorted(chord_a), sorted(chord_b)))
    
    def has_parallel_faults(self, chord_a: List[int], chord_b: List[int]) -> bool:
        """
        Scans transitions for parallel fifths (7 semitones) or octaves (12 semitones).
        Returns True if a structural violation occurs.
        """
        sorted_a = sorted(chord_a)
        sorted_b = sorted(chord_b)

        for i in range(len(sorted_a)):
            for j in range(i + 1, len(sorted_a)):
                interval_a = (sorted_a[j] - sorted_a[i]) % 12
                interval_b = (sorted_b[j] - sorted_b[i]) % 12

                if interval_a in [0, 7] and interval_a == interval_b:
                    motion_i = sorted_b[i] - sorted_a[i]
                    motion_j = sorted_b[j] - sorted_a[j]
                    if motion_i == motion_j and motion_i != 0:
                        return True
        
        return False
    
    def generate_candidates(self, base_chord: List[int]) -> List[List[int]]:
        """
        Algorithmically generates ascending and descending inversions in-memory 
        from a verified SQL root pitch array.
        """
        if not base_chord:
            return []
        
        candidates = [sorted(base_chord)]

        # Ascending Inversions (Shift lowest note up an octave)
        current_asc = sorted(base_chord)
        for _ in range(len(base_chord) - 1):
            next_asc = current_asc[1:] + [current_asc[0] + 12]
            current_asc = sorted(next_asc)
            candidates.append(current_asc)
        
        # Descending Inversions (Shift highest note down an octave)
        current_desc = sorted(base_chord)
        for _ in range(len(base_chord) - 1):
            next_desc = [current_desc[-1] - 12] + current_desc[:-1]
            current_desc = sorted(next_desc)
            candidates.append(current_desc)
        
        return candidates

    def optimize_transition(self, current_chord: List[int], target_candidates: List[List[int]]) -> List[int]:
        """
        Evaluates candidate inversions for the target chord and selects
        the mathematically optimal state.
        """
        best_candidate = target_candidates[0]
        min_cost = float('inf')

        for candidate in target_candidates:
            if self.has_parallel_faults(current_chord, candidate):
                continue

            cost = self.calculate_distance(current_chord, candidate)
            if cost < min_cost:
                min_cost = cost
                best_candidate = candidate

        return sorted(best_candidate)
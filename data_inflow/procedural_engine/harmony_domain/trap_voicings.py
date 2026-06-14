from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType
from data_inflow.procedural_engine.harmony_domain.voice_leading import VoiceLeader
from database.models import Chord, ChordNote 

class TrapVoicing(BaseProceduralConcept):
    def __init__(self):
        super().__init__(domain_type=DomainType.HARMONY, concept_tag="TRAP_VOICING")
        self.voice_leader = VoiceLeader()

    def fetch_verified_root(self, session: Session, target_chord_name: str) -> List[int]:
        """
        Queries the static SQL library for the verified root pitch array.
        Mathematically enforces that only is_verified == True records are pulled.
        """
        stmt = (
            select(ChordNote.pitch_value)
            .join(Chord)
            .where(Chord.chord_name == target_chord_name)
            .where(Chord.is_verified == True)
        )
        
        results = session.execute(stmt).scalars().all()
        
        if not results:
            raise ValueError(f"Schema Violation: Chord '{target_chord_name}' is either unverified or missing from the database.")
            
        return sorted(list(results))

    def enforce_trap_heuristics(self, pitch_array: List[int]) -> List[int]:
        """
        Pre-optimization hook. Translates legacy dictionary logic into raw integer 
        mutations to strip bass 3rds and compress upper-register 2nds.
        """
        mutated_pitches = set()
        
        for pitch in pitch_array:
            if pitch < 48:
                pitch_class = pitch % 12
                # If minor 3rd (3) or major 3rd (4), strip down to root
                if pitch_class in [3, 4]:
                    pitch = pitch - pitch_class
            elif pitch >= 60:
                pitch_class = pitch % 12
                # If major 2nd (2), compress to minor 2nd (1)
                if pitch_class == 2:
                    pitch = pitch - 1
                    
            mutated_pitches.add(pitch)
            
        return sorted(list(mutated_pitches))

    def process_progression(self, session: Session, markov_progression: List[str]) -> List[List[int]]:
        """
        Executes the full polyphonic optimization pipeline.
        Transforms an array of string chord names into trap-constrained, voice-led MIDI arrays.
        """
        if not markov_progression:
            return []

        final_midi_arrays = []
        
        # Step 0: Initialize and mutate the first chord
        first_chord_name = markov_progression[0]
        raw_first_root = self.fetch_verified_root(session, first_chord_name)
        current_chord = self.enforce_trap_heuristics(raw_first_root)
        final_midi_arrays.append(current_chord)

        # Route the remaining progression through the constraint and VoiceLeader chain
        for target_chord_name in markov_progression[1:]:
            
            # Step 1: Query the SQL database for the validated root array
            raw_target_root = self.fetch_verified_root(session, target_chord_name)
            
            # Step 2: Apply Trap Domain constraints (The Pre-Optimization Hook)
            target_root_array = self.enforce_trap_heuristics(raw_target_root)
            
            # Step 3: Manually instantiate the 2D inversion matrix via VoiceLeader
            target_candidates = self.voice_leader.generate_candidates(target_root_array)
            
            # Step 4: Execute the mathematical transition
            optimized_chord = self.voice_leader.optimize_transition(current_chord, target_candidates)
            
            final_midi_arrays.append(optimized_chord)
            current_chord = optimized_chord 

        return final_midi_arrays
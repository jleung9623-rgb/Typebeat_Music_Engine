from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType
from database.models import Chord

class ModalInterchange(BaseProceduralConcept):
    def __init__(self):
        super().__init__(domain_type=DomainType.HARMONY, concept_tag="MODAL_INTERCHANGE")

    def verify_chord_exists(self, session: Session, chord_name: str) -> bool:
        """
        Checks the live SQL schema to mathematically guarantee the borrowed chord
        is structurally verified before allowing the substitution.
        """
        stmt = select(Chord.id).where(
            Chord.chord_name == chord_name,
            Chord.is_verified == True
        )
        result = session.execute(stmt).first()
        return result is not None
    
    def calculate_note_parallel(self, chord_name: str) -> Optional[str]:
        """
        Parses the nomenclature to calculate the parallel minor equivalent of a major note.
        Expects nomenclature format: 'Root-Class' (e.g., 'C-Major' -> 'C-Minor').
        """
        parts = chord_name.split('-')
        if len(parts) <2:
            return None
        
        root = parts[0]
        chord_class = '-'.join(parts[1:])

        # Strictly substitutes Major structures to Minor equivalents
        if chord_class == "Major":
            return f"{root}-Minor"
        elif chord_class == "Major-7th":
            return f"{root}-Minor-7th"
        
        return None
    
    def process_progression(self, session: Session, markov_progression: List[str], substitution_indices: List[int]) -> List[str]:
        """
        Intercepts the raw string progression and mutates specific indices 
        into their parallel minor equivalents, strictly validated against the SQL schema.
        """
        if not markov_progression:
            return []
        
        mutated_progression = markov_progression.copy()

        for index in substitution_indices:
            if index >= len(mutated_progression):
                continue

            original_chord = mutated_progression[index]
            parallel_minor = self.calculate_note_parallel(original_chord)

            if parallel_minor and self.verify_chord_exists(session, parallel_minor):
                mutated_progression[index] = parallel_minor
            # If the schema rejects the parallel minor, the substitution is mathematically aborted to prevent crashes.
        
        return mutated_progression
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from data_inflow.procedural_engine.core_generator import BaseProceduralConcept, DomainType
from database.models import Scale, track_scale_map

class PassingTones(BaseProceduralConcept):
    def __init__(self, target_gap_duration: float = 1.0, lead_channel: int = 2):
        """
        Calculates diatonic passing notes to bridge melodic gaps.
        """
        super().__init__(domain_type=DomainType.MELODIC, concept_tag="PASSING_TONES")
        self.target_gap_duration = target_gap_duration
        self.lead_channel = lead_channel
    
    def generate_diatonic_array(self, session: Session, track_id: int) -> List[int]:
        """Queries the SQL schema to extract the assigned scale intervals."""
        
        # STRICT CORRECTION: Projecting exact columns to return a strict tuple, bypassing ORM typing
        stmt = (
            select(Scale.default_root_note, Scale.intervals)
            .join(track_scale_map, Scale.id == track_scale_map.c.scale_id)
            .where(track_scale_map.c.track_id == track_id)
        )
        # We remove .scalars() so it returns a Row tuple containing exactly (default_root_note, intervals)
        scale_record = session.execute(stmt).first()

        if not scale_record:
            # Fallback to standard C-Minor if schema fails, preventing hard crashes
            return [0, 2, 3, 5, 7, 8, 10]

        # scale_record[0] is strictly recognized as an integer by the DB driver
        # scale_record[1] is strictly recognized as a string
        root_note = int(scale_record[0]) 
        interval_string = scale_record[1]

        interval_steps = [int(i) for i in interval_string.split(',')]
        
        valid_pitches = []
        current_pitch = root_note % 12
        
        while current_pitch < 128:
            valid_pitches.append(current_pitch)
            for step in interval_steps:
                current_pitch += step
                if current_pitch < 128:
                    valid_pitches.append(current_pitch)
                    
        return sorted(list(set(valid_pitches)))
    
    def find_passing_pitch(self, start_pitch: int, end_pitch: int, valid_pitches: List[int]) -> int:
        """Calculates the optimal diatonic midprint between two structural pitches."""
        if start_pitch == end_pitch:
            return start_pitch
        
        diatonic_subset = [p for p in valid_pitches if min(start_pitch, end_pitch) < p < max(start_pitch, end_pitch)]

        if not diatonic_subset:
            return start_pitch
        
        mid_index = len(diatonic_subset) // 2
        return diatonic_subset[mid_index]
    
    def apply_melodic_path(self, session: Session, track_id: int, temporal_matrix: List[Dict]) -> List[Dict]:
        """Isolates monophonic anchors, interpolates passing ontes, and appends the new track."""
        if not temporal_matrix:
            return temporal_matrix
        
        valid_pitches = self.generate_diatonic_array(session, track_id)

        # 1. Monophonic Anchor Extraction
        grouped_beats = {}
        for note in temporal_matrix:
            beat = note['beat_position']
            if beat not in grouped_beats:
                grouped_beats[beat] = []
            grouped_beats[beat].append(note)
        
        sorted_beats = sorted(grouped_beats.keys())
        lead_anchors = []

        for beat in sorted_beats:
            chord_notes = grouped_beats[beat]
            highest_note = max(chord_notes, key=lambda x: x['pitch_value'])

            # Create isolated clone for Channel 2
            lead_note = highest_note.copy()
            lead_note['midi_channel'] = self.lead_channel
            lead_anchors.append(lead_note)

        if len(lead_anchors) < 2:
            return temporal_matrix
        
        # 2. Linear Interpolation
        interpolated_lead = []
        for i in range(len(lead_anchors) - 1):
            current_note = lead_anchors[i]
            next_note = lead_anchors[i + 1]

            if current_note['duration'] > self.target_gap_duration:
                pitch_distance = abs(current_note['pitch_value'] - next_note['pitch_value'])
                if pitch_distance >= 2:
                    original_duration = current_note['duration']
                    sliced_duration = round(original_duration / 2.0, 3)

                    current_note['duration'] = sliced_duration
                    interpolated_lead.append(current_note)

                    passing_pitch = self.find_passing_pitch(current_note['pitch_value'], next_note['pitch_value'], valid_pitches)

                    bridging_note = {
                        "pitch_value": passing_pitch,
                        "beat_position": round(current_note['beat_position'] + sliced_duration, 3),
                        "duration": sliced_duration,
                        "micro_offset": 0.0,
                        "midi_channel": self.lead_channel
                    }
                    interpolated_lead.append(bridging_note)
                    continue

            interpolated_lead.append(current_note)

        interpolated_lead.append(lead_anchors[-1])

        # 3. Flat Array Extension (ADR 0024 Compliance)
        master_matrix = temporal_matrix.copy()
        master_matrix.extend(interpolated_lead)

        return master_matrix
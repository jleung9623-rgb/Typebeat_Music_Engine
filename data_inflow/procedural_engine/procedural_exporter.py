import os
import math
import pandas as pd
from typing import List, Dict
from database.models import SectionClass

class ProceduralExporter:
    """
    Ingests flat dictionary matrices from the ProceduralOrchestrator and
    formats them into strictly compliant DataFrames for motifs_upload.py.
    """
    def __init__(self, output_dir: str = "extracted_csvs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.grid_resolution = 1.0

    def export_motif_to_csv(self, motif_matrix: List[Dict], base_filename: str, motif_class: SectionClass, phrase_latency: float = 0.0) -> str:
        """
        Calculates boundary metadata and writes the matrix to disk.
        """
        if not motif_matrix:
            raise ValueError("Schema Violation: Cannot export an empty motif matrix.")

        # 1. Calculate Boundaries (Strictly mirroring midi_extractor.py math)
        last_beat = max((n['beat_position'] + n['duration']) for n in motif_matrix)
        grid_boundary = math.ceil(last_beat / self.grid_resolution) * self.grid_resolution
        
        rest_duration = round(grid_boundary - last_beat, 3)
        rest_suffix = f"REST_{rest_duration}" if rest_duration > 0 else "NONE"
        pivot_offset = round(last_beat, 3)

        # 2. Inject Required Relational Metadata
        formatted_rows = []
        for note in motif_matrix:
            formatted_note = note.copy()
            formatted_note['motif_name'] = base_filename
            formatted_note['motif_class'] = motif_class.name
            formatted_note['motif_pivot_offset'] = pivot_offset
            formatted_note['rest_duration'] = rest_duration
            formatted_note['rest_suffix'] = rest_suffix
            formatted_note['phrase_latency'] = phrase_latency
            formatted_rows.append(formatted_note)

        # 3. Cast to DataFrame and Enforce Column Order
        df = pd.DataFrame(formatted_rows)
        
        # Enforcing the exact required columns for motifs_upload.py
        target_columns = [
            'motif_name', 'motif_class', 'motif_pivot_offset', 
            'rest_duration', 'rest_suffix', 'phrase_latency', 
            'pitch_value', 'beat_position', 'duration', 'micro_offset'
        ]
        
        # We append 'velocity' and 'midi_channel' at the end to prevent DataFrame KeyError, 
        # allowing motifs_upload to simply ignore them if it doesn't need them.
        for col in ['velocity', 'midi_channel']:
            if col in df.columns:
                target_columns.append(col)

        df = df[target_columns]
        
        # 4. Write to Disk
        output_path = os.path.join(self.output_dir, f"{base_filename}.csv")
        df.to_csv(output_path, index=False)
        
        return output_path
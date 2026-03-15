from database.connection import SessionLocal
from database.models import Chord, ChordNote, Scale

class HarmonicMap:

    def seed_basic_chords(self):
        # Open session using centralized foundation
        session = SessionLocal()

        # Initializaiton: Note-Level Harmonic Elements (Sets base midi value at 60 for Middle C)
        roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        base_midi = 60

        chord_formulas = {
            #Triads
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Diminished": [0, 3, 6],
            "Augmented": [0, 4, 8],

            # Suspended Chords
            "Sus2": [0, 2, 7],
            "Sus4": [0, 5, 7],

            # Sevenths
            "Major-7th": [0, 4, 7, 11],
            "Minor-7th": [0, 3, 7, 10],
            "Dominant-7th": [0, 4, 7, 10],
            "Half-Diminished-7th": [0, 3, 6, 10],

            # Power Chords
            "Power-5th": [0, 7]
        }

        print("Seeding Chord Dictionary using centralized connection...")
        chords_added = 0

        try:
            for i, root in enumerate(roots):
                root_note = base_midi + i

                for chord_type, intervals in chord_formulas.items():

                    # Create chord entry
                    new_chord = Chord(
                        chord_name = f"{root}-{chord_type}",
                        chord_class = chord_type,
                        is_verified = True
                    )

                    new_chord.chord_notes = [
                        ChordNote(pitch_value = root_note + interval)
                        for interval in intervals
                    ]
            
                    session.add(new_chord)
                    chords_added += 1

            session.commit()
            print(f"SUCCESS: {chords_added} unique chords and their respective notes seeded.")

        except Exception as e:
            session.rollback()
            print(f"Error executing chord seeding process: {e}")
        finally:
            session.close()

    def seed_scales(self):
        # Open session using centralized foundation
        session = SessionLocal()

        scale_formulas = {
            # Foundational Scales (7-Note)
            "Major (Ionian)": "2,2,1,2,2,2,1",
            "Natural Minor (Aeolian)": "2,1,2,2,1,2,2",
            "Harmonic Minor": "2,1,2,2,1,3,1",
            "Melodic Minor": "2,1,2,2,2,2,1",

            # Folk, Rock, & Blues Scales
            "Major Pentatonic": "2,2,3,2,3",
            "Minor Pentatonic": "3,2,2,3,2",
            "Blues Scale": "3,2,1,1,3,2",

            # Other Modal Scales
            "Dorian": "2,1,2,2,2,1,2",
            "Phrygian": "1,2,2,2,1,2,2",
            "Lydian": "2,2,2,1,2,2,1",
            "Mixolydian": "2,2,1,2,2,1,2",
            "Locrian": "1,2,2,1,2,2,2",

            # Symmetrical & Atonal Scales
            "Chromatic": "1,1,1,1,1,1,1,1,1,1,1,1",
            "Whole Tone": "2,2,2,2,2,2",
            "Diminished (W-H)": "2,1,2,1,2,1,2,1",

            # Exotic Scales
            "Harmonic Major": "2,2,1,2,1,3,1",
            "Hungarian Minor": "2,1,3,1,1,3,1"
        }

        print("Seeding Scales Dictionary using centralized connection...")
        scales_added = 0

        try:
            for name, intervals in scale_formulas.items():
                new_scale = Scale(
                    scale_name = name,
                    default_root_note = 60, # Middle C Default
                    intervals = intervals
                )
                session.add(new_scale)
                scales_added += 1

            session.commit()
            print(f"SUCCESS: {scales_added} unique scales seeded.")

        except Exception as e:
            session.rollback()
            print(f"Error executing scales seeding process: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    mapper = HarmonicMap()

    print("--- STARTING HARMONIC MAP SEEDING ---")
    mapper.seed_basic_chords()
    mapper.seed_scales()
    print("--- HARMONIC SEEDING COMPLETE ---")
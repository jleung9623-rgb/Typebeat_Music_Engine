from database.models import Motif, MotifNote, track_motif_map, Transition
from engine.aliases import BLUEPRINT_BLOCK_LENGTHS
from sqlalchemy import func
import random


def run_generator(session, generation_payload):
    """
    Executes the generation of the composition's motif timeline.
    Ordered based on song structure defined by blueprint blocks.
    """

    # Initializes the master timeline container before iterating through each track to generate their respective timelines based on the motifs available to them.
    master_timeline = {}

    for track in generation_payload['tracks']:
        
        # Initializes the current ID and timeline container for each track to be added to the master_timeline
        current_track_id = track['track_id']
        track_timeline = []
        
        # Resets the motif state memory for each new track
        motif_id_temp = None

        print(f"Generating Markov chain for Track ID: {current_track_id}")

        # Iterates through blueprint blocks defined in the generation payload, generating a motif timeline for each block and appending it to the master timeline.
        for blueprint_block in generation_payload['blueprints']:
                
            # Generates a motif block timeline segment based on the parent track, motif class, and active motif ID
            block_timeline = generate_timeline(
                session = session,
                track_id = current_track_id,
                blueprint_block = blueprint_block,
                active_motif_id = motif_id_temp
            )

            # Adds the generated timeline block to the end of the list to ensure sequential consistency based on 'block_position' order
            track_timeline.extend(block_timeline)

            # If track timeline has been populated with a segment, caches its data as the last item in the list to create a 'state' for the next iteration to use as reference
            if track_timeline:
                motif_id_temp = track_timeline[-1]

        # Adds each track's generated timeline to the final master timeline output
        master_timeline[current_track_id] = track_timeline
        
    return master_timeline


def generate_timeline(session, track_id, blueprint_block, active_motif_id=None):
    """
    Generates a motif timeline segment based on the parent track, motif class, and active motif ID.
    Keeps track of the segment's current temporal position to ensure the final timeline segment reaches the target beat length designated by the blueprint block.
    """

    # Initializes the timeline segment for the current blueprint block
    timeline = []
    
    # Initializes the 'clock' for the current block, including the current temporal location and the total length of the block (Both in beats)
    current_beats = 0

    # Initializes the classification for the current block based on its blueprint
    blueprint_block = blueprint_block['block_class']

    # Grabs the length of each blueprint block based on its class
    target_beats = BLUEPRINT_BLOCK_LENGTHS.get(blueprint_block, 16.0)

    # Selects motifs to use within the block container until the target beat length is reached
    while current_beats < target_beats:
        next_id = select_motif(
            session = session,
            track_id = track_id,
            blueprint_block = blueprint_block,
            current_motif_id = active_motif_id
        )
        
        # Checks if motif generation no longer detects a valid transition, halting block generation if condition is reached
        if next_id is None:
            print(f"Dead end reached. Halting block generation.")
            break
        
        # Initializes the selected motif's duration, returning an error if the value is non-positive
        motif_duration = get_motif_duration(session, motif_id=next_id)

        if motif_duration <= 0:
            print(f"WARNING: Motif with ID {next_id} has a non-positive duration. Skipping motif.")
            continue

        # Advances the 'clock' of the current timeline segment based on duration of the selected motif
        current_beats += motif_duration
        
        # Caches the state of the current motif ID to be used as reference for the upcoming next motif
        active_motif_id = next_id
        
        # Adds the final motif data to the final timeline segment object
        timeline.append(active_motif_id)

    return timeline


def select_motif(session, track_id, blueprint_block, current_motif_id=None):
    """
    Selects the motif either as a starting point based on the track and block class or as a transition based on the current motif ID.
    Uses weighted randomness for selection in both cases.
    """

    # If there is no motif ID available for selection, selects one at random
    if current_motif_id is None:

        # Fetches motif options based on their parent track and the designated blueprint block/motif class
        seed_options = session.query(Motif.id, track_motif_map.c.selection_weight).join(track_motif_map).filter(track_motif_map.c.track_id == track_id, Motif.motif_class == blueprint_block).all()

        # Checks if there are available motif options to choose from, returning a dead end for current block's generation if not
        if not seed_options:
            return None
        
        # Unpack motif IDs and selection weighting values for selection
        options = [opt.id for opt in seed_options]
        weights = [opt.selection_weight for opt in seed_options]
        
        # Selects the next motif ID based on weighted randomness
        return random.choices(options, weights=weights, k=1)[0]
    
    # If there is an active motif ID to select, selects the next motif to use based on transitional data
    else:

        # Fetches valid transition paths based on the current motif ID
        valid_paths = session.query(Transition.to_motif_id, Transition.transition_weight).filter(Transition.from_motif_id == current_motif_id).all()

        # Checks if there are available paths to choose from, returning a dead end for current block's generation if not
        if not valid_paths:
            return None
        
        options = [path.to_motif_id for path in valid_paths]
        weights = [path.transition_weight for path in valid_paths]

        return random.choices(options, weights=weights, k=1)[0]          


def get_motif_duration(session, motif_id):
    """Obtains the motif duration by finding the furthest beat position reached after the final motif note's duration ends."""

    # Queries the designated Motif ID, returning a set endpoint for the motif if available
    motif = session.query(Motif).filter(Motif.id == motif_id).first()

    if motif and motif.motif_pivot_offset > 0.0:
        return motif.motif_pivot_offset

    # If set endpoint doesn't exist, sums each motif note's beat position and duration to find their endpoint, selecting the highest value out of the sums and returning the float as a singular value
    max_beats = session.query(
        func.max(MotifNote.beat_position + MotifNote.duration)
    ).filter(MotifNote.motif_id == motif_id).scalar()

    return max_beats or 0.0
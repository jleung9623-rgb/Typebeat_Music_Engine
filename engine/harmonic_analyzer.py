from database.models import MotifNote, Motif, track_motif_map

def map_pitch_to_scale(raw_pitch, target_root, target_intervals):
    """
    Maps the raw pitch value of a motif note to a new pitch value based on the target scale defined by the track profile.
    Assumes a default scale of C major to provide a stable frame of reference for mapping the raw pitch to the target scale.
    """

    # Initializes the default scale and semitone intervals
    default_root = 60
    default_intervals = [0, 2, 4, 5, 7, 9, 11]

    # Initializes the list of target semitone intervals to be mapped onto new pitch, and the current interval being iterated upon
    target_values = [0]
    current_interval = 0

    # Iterates through the target intervals, building a pitch array by summing each interval's semitone steps
    for step in target_intervals[:-1]:
        current_interval += step
        target_values.append(current_interval)

    # Calculates the pitch delta between the motif note's raw pitch and the default root note of 60 (Middle C)
    pitch_delta = raw_pitch - default_root

    # Calculates how many octaves up the current pitch should be
    octave_shift = pitch_delta // 12
    
    # Calculates the origin interval of the raw pitch
    interval_class = pitch_delta % 12

    # If origin interval exists within the default scale, finds the array coordinates with equivalent interval from the target scale and extracts it
    if interval_class in default_intervals:
        interval_index = default_intervals.index(interval_class)
        final_interval_class = target_values[interval_index]
    
    # If origin interval does not exist in default scale, it is used as the final interval
    else:
        final_interval_class = interval_class
    
    # Calculates the new pitch of the scale
    new_pitch = target_root + final_interval_class + (octave_shift * 12)

    return new_pitch


def transpose_motif(session, master_timeline, track_profile):
    """Transposes each motif in the composition timeline before assigning it to the final MIDI output as a dictionary package."""

    # Initializes the container for final MIDI data output
    final_midi_data = []

    # Initializes global 'clock' to keep track of current temporal position
    current_song_beat = 0.0

    # Retrieves the track-specific origin data for use in the final MIDI output
    track_id = track_profile.get('track_id')

    if not track_id:
        raise ValueError("ERROR: track_id missing from track_profile. Cannot query junction modifiers.")

    target_root = track_profile.get('default_root_note')
    target_intervals = track_profile.get('intervals')
    midi_channel = track_profile.get('midi_channel')

    # Iterates through each motif in the composition timeline, mapping track-level pitch data before applying transposition
    for motif_id in master_timeline:

        # Fetches the phrase latency of each motif used to calculate the absolute timing of the timeline
        motif_record = session.query(Motif).filter(Motif.id == motif_id).first()
        phrase_latency = motif_record.phrase_latency if motif_record else 0.0

        # Fetches the notes for all motifs within the timeline to be transposed, skipping over the motif if it has no notes
        motif_notes = session.query(MotifNote).filter(MotifNote.motif_id == motif_id).all()
        
        if not motif_notes:
            continue

        # Fetches the motif-level transposition value
        shift_scalar = session.query(track_motif_map.c.octave_shift).filter(
            track_motif_map.c.track_id == track_id,
            track_motif_map.c.motif_id == motif_id
        ).scalar()
        motif_octave_shift = shift_scalar if shift_scalar else 0

        # Initializes the maximum possible motif beat length as a scalar used to advance the global clock
        max_motif_beat = 0.0

        # Iterates through each motif, transposing them before assigning them to the final MIDI output
        for note in motif_notes:

            # Bypasses transposition for percussion instruments which are assigned to MIDI channel 10
            if midi_channel == 10:
                final_pitch = note.pitch_value
            else:
                # Applies track-level transposition before motif-level transposition to calculate the final pitch
                transposed_pitch = map_pitch_to_scale(note.pitch_value, target_root, target_intervals)

                # Keeps final pitch in a range of 127 to account for the frequency limitations of standard synthesizers and MIDI readers
                final_pitch = max(0, min(127, transposed_pitch + (motif_octave_shift * 12)))

            # Calculates the absolute current time
            absolute_beat = current_song_beat + note.beat_position + phrase_latency

            # Calculates the motif duration to advance the global clock
            note_end = note.beat_position + note.duration
            if note_end > max_motif_beat:
                max_motif_beat = note_end

            # Assigns a motif, its parent track's MIDI channel, the transposed pitch, and its temporal data to the final MIDI output container
            final_midi_data.append({
                'motif_id': motif_id,
                'midi_channel': midi_channel,
                'pitch': final_pitch,
                'beat_position': absolute_beat,
                'duration': note.duration,
                'micro_offset': note.micro_offset
            })

        # Advances global clock
        current_song_beat += max_motif_beat

    return final_midi_data

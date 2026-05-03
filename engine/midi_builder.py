import re
import os
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

def sanitize_filename(name):
    """Filters any ineligible characters from filename input to prevent file system errors; allows only letters, numbers, dashes, underscores, and periods"""

    return re.sub(r'(?u)[^-\w.]', '', name) # Regex expression to filter any other exceptional character besides '-\w'


def build_midi_file(global_midi_data, file_name, metadata, output_dir):
    """
    Translates absolute mathematical pitch/beat data into sequential MIDI delta times.
    Writes the .mid file to the designated directory.
    """

    # 1. Establish Configuration
    ticks_per_beat = 480
    bpm = metadata.get('default_tempo', 120)
   
    s_file_name = sanitize_filename(file_name)
    final_file_name = f"{s_file_name}.mid"

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, final_file_name)

    # 2. Initialize the MIDI Object
    mid = MidiFile(ticks_per_beat=ticks_per_beat)

    # 3. Build the Meta Track (Conductor Track)
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    # 4. Group Events by MIDI Channel
    channel_data = {}
    for event in global_midi_data:
        channel = event['midi_channel']
        if channel not in channel_data:
            channel_data[channel] = []
        channel_data[channel].append(event)

    # 5. Convert Absolute Time to Delta Time per Channel
    for channel, events in channel_data.items():
        track = MidiTrack()
        mid.tracks.append(track)

        mido_channel = channel - 1
        
        midi_events = []
        for note in events:
            start_ticks = int((note['beat_position'] + note.get('micro_offset', 0.0)) * ticks_per_beat)
            end_ticks = int((note['beat_position'] + note.get('micro_offset', 0.0) + note['duration']) * ticks_per_beat)

            pitch = int(note['pitch'])

            midi_events.append({'type': 'note_on', 'time': start_ticks, 'pitch': pitch, 'velocity': 100})
            midi_events.append({'type': 'note_off', 'time': end_ticks, 'pitch': pitch, 'velocity': 0})

        midi_events.sort(key=lambda x: x['time'])

        current_ticks = 0
        for ev in midi_events:
            delta_ticks = ev['time'] - current_ticks
            track.append(Message(
                ev['type'],
                channel = mido_channel,
                note = ev['pitch'],
                velocity = ev['velocity'],
                time = delta_ticks
            ))

            current_ticks = ev['time']

    # 6. Render File
    mid.save(file_path)

    return file_path, final_file_name
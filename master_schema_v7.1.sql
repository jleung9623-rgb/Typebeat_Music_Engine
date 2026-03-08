-- ==========================================
-- TYPEBEAT AI V7.1 - MASTER SCHEMA (FINAL HARDENED)
-- ==========================================

-- Global Style Rules
CREATE TABLE genres (
    genre_id INT PRIMARY KEY AUTO_INCREMENT,
    genre_name VARCHAR(50) NOT NULL,
    default_tempo INT,
    time_signature VARCHAR(10),
    entropy_pivot_bar INT
);

-- Specialist Artist Profiles
CREATE TABLE artists (
    artist_id INT PRIMARY KEY AUTO_INCREMENT,
    artist_name VARCHAR(50) NOT NULL,
    genre_id INT,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Persistence Record
CREATE TABLE compositions (
    comp_id INT PRIMARY KEY AUTO_INCREMENT,
    artist_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

-- UI & Tool State 
CREATE TABLE user_preferences (
    pref_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(50) NOT NULL,
    setting_value VARCHAR(100)
);

-- Scales & Pitch Sets
CREATE TABLE scales (
    scale_id INT PRIMARY KEY AUTO_INCREMENT,
    scale_name VARCHAR(50) NOT NULL,
    intervals VARCHAR(50) NOT NULL,
    default_root_note INT
);

-- Chord Definitions
CREATE TABLE chords (
    chord_id INT PRIMARY KEY AUTO_INCREMENT,
    chord_name VARCHAR(28) NOT NULL,
    chord_class VARCHAR(50)
);

-- Note Intervals within Chords
CREATE TABLE chord_notes (
    note_id INT PRIMARY KEY AUTO_INCREMENT,
    chord_id INT NOT NULL,
    FOREIGN KEY (chord_id) REFERENCES chords(chord_id)
);

-- Song Structures
CREATE TABLE song_blueprints (
    blueprint_id INT PRIMARY KEY AUTO_INCREMENT,
    genre_id INT NOT NULL,
    block_position INT NOT NULL,
    block_class ENUM('Opening', 'Verse', 'Pre-Chorus', 'Chorus', 'Build', 'De-escalation', 'Bridge', 'Entropic', 'Rest', 'Outro') NOT NULL,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Individual Track Configurations
CREATE TABLE tracks (
    track_id INT PRIMARY KEY AUTO_INCREMENT,
    track_name VARCHAR(50) NOT NULL,
    midi_channel INT NOT NULL,
    instrument_name VARCHAR(50),
    patch_number INT,
    genre_id INT,
    track_motif_limit INT,
    scale_id INT,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
    FOREIGN KEY (scale_id) REFERENCES scales(scale_id)
);

-- Motifs (The Building Blocks)
CREATE TABLE motifs (
    motif_id INT PRIMARY KEY AUTO_INCREMENT,
    motif_name VARCHAR(50),
    sequence_data VARCHAR(100),
    phrase_latency FLOAT,
    motif_weight FLOAT,
    occurrence_count INT,
    motif_class ENUM('Opening', 'Verse', 'Pre-Chorus', 'Chorus', 'Build', 'De-escalation', 'Bridge', 'Entropic', 'Rest', 'Outro'),
    track_id INT,
    motif_pivot_offset FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

-- Markov Transitions
CREATE TABLE transitions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    from_motif_id INT NOT NULL,
    to_motif_id INT NOT NULL,
    weight FLOAT NOT NULL,
    FOREIGN KEY (from_motif_id) REFERENCES motifs(motif_id),
    FOREIGN KEY (to_motif_id) REFERENCES motifs(motif_id)
);

-- Granular MIDI Data
CREATE TABLE motif_notes (
    note_id INT PRIMARY KEY AUTO_INCREMENT,
    motif_id INT NOT NULL,
    pitch_value INT NOT NULL,
    chord_id INT,
    duration FLOAT,
    beat_position FLOAT,
    micro_offset FLOAT,
    FOREIGN KEY (motif_id) REFERENCES motifs(motif_id),
    FOREIGN KEY (chord_id) REFERENCES chords(chord_id)
);
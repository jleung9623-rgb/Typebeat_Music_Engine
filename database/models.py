import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Enum, TIMESTAMP, Text, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, DeclarativeBase

# Class Enums: Define the expected labels for each type of motif, blueprint, and track

class SectionClass(enum.Enum):
    OPENING = "Opening"
    VERSE = "Verse"
    VERSE_B = "Verse-B"
    PRE_CHORUS = "Pre-Chorus"
    CHORUS = "Chorus"
    CHORUS_B = "Chorus-B"
    CHORUS_FINAL = "Chorus-Final"
    BUILD = "Build"
    DE_ESCALATION = "De-Escalation"
    BRIDGE = "Bridge"
    ENTROPIC = "Entropic"
    REST = "Rest"
    OUTRO = "Outro"

class TrackClass(enum.Enum):
    KICK = "Kick"
    SNARE = "Snare"
    HIHAT = "HiHat"
    PERCUSSION = "Percussion"
    BASS = "Bass"
    MELODIC_LEAD = "Melodic_Lead"
    PAD_ATMOSPHERE = "Pad_Atmosphere"
    FX = "FX"

# Initializes relationship with Alembic through its use in env.py
class Base(DeclarativeBase):
    pass

# Junction Tables: Handles Many-to-Many (M:N) relationships where data is ideally interchangeable

artist_genre_map = Table(
    'artist_genre_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id', ondelete="CASCADE"), nullable=False),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete="CASCADE"), nullable=False),
    Column('affinity_score', Float, default=1.0, server_default="1.0"),     # Likelihood of artist to be selected for next generated song
    UniqueConstraint('artist_id', 'genre_id', name='uix_artist_genre')
)

genre_blueprint_map = Table(
    'genre_blueprint_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete="CASCADE"), nullable=False),
    Column('blueprint_id', Integer, ForeignKey('song_blueprints.id', ondelete="CASCADE"), nullable=False),
    UniqueConstraint('genre_id', 'blueprint_id', name='uix_genre_blueprint')
)

genre_track_map = Table(
    'genre_track_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete="CASCADE"), nullable=False),
    Column('track_id', Integer, ForeignKey('tracks.id', ondelete="CASCADE"), nullable=False),
    Column('selection_weight', Float, nullable=False, default=1.0, server_default="1.0"),
    UniqueConstraint('genre_id', 'track_id', name='uix_genre_track')
)

track_motif_map = Table(
    'track_motif_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('track_id', Integer, ForeignKey('tracks.id', ondelete="CASCADE"), nullable=False),
    Column('motif_id', Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False),
    Column('selection_weight', Float, nullable=False, default=1.0, server_default="1.0"),   # Probability of motif being selected for current track
    Column('octave_shift', Integer, nullable=False, default=0, server_default="0"),         # Transposition modifier (Change in MIDI note pitch) on motifs to be used for current track
    UniqueConstraint('track_id', 'motif_id', name='uix_track_motif')
)

track_scale_map = Table(
    'track_scale_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('track_id', Integer, ForeignKey('tracks.id', ondelete="CASCADE"), nullable=False),
    Column('scale_id', Integer, ForeignKey('scales.id', ondelete="CASCADE"), nullable=False),
    Column('is_default', Boolean, default=False, server_default="0"),   # Filter for default scale of current track
    UniqueConstraint('track_id', 'scale_id', name='uix_track_scale')
)

# Main Tables: Defines the core faculties of the Typebeat Database

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    artist_name = Column(String(100), nullable=False) # Name label of current artist

    compositions = relationship("Composition", back_populates='artist')
    genres = relationship("Genre", secondary=artist_genre_map, back_populates="artists")

class Chord(Base):
    __tablename__ = 'chords'
    id = Column(Integer, primary_key=True)
    chord_name = Column(String(28), nullable=False)     # Name label of current chord
    chord_class = Column(String(50), nullable=False)    # Chord type of current chord (Major, Minor, Power, etc.)
    is_verified = Column(Boolean, nullable=False, default=False, server_default="0")    # Filter for verified (useable) chord combinations within the SQL database library (The 'static library')

    chord_notes = relationship("ChordNote", back_populates="chord", cascade="all, delete-orphan")
    motif_notes = relationship("MotifNote", back_populates="chord")

class ChordNote(Base):
    __tablename__ = 'chord_notes'
    id = Column(Integer, primary_key=True)
    chord_id = Column(Integer, ForeignKey('chords.id', ondelete="CASCADE"), nullable=False)
    pitch_value = Column(Integer, nullable=False)   # MIDI value for current chord note

    chord = relationship("Chord", back_populates="chord_notes")

class Composition(Base):
    __tablename__ = 'compositions'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id', ondelete="SET NULL"), nullable=True)   # Preserves composition record if artist is deleted
    file_path = Column(String(255), nullable=False)             # Save path for generated MIDI composition
    file_name = Column(String(255), nullable=False)             # Save name for generate MIDI composition
    created_at = Column(TIMESTAMP, server_default=func.now())   # Log for creation timestamp of MIDI composition (Allows the DB to handle the timestamp automatically)

    artist = relationship("Artist", back_populates="compositions")

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    genre_name = Column(String(50), unique=True, nullable=False)    # Name label of current genre
    default_tempo = Column(Integer, nullable=False)                 # Base tempo of genre (In BPM)
    time_signature = Column(String(10), nullable=False)             # Base time signature (4/4, 3/4, etc.) of genre

    artists = relationship("Artist", secondary=artist_genre_map, back_populates="genres")
    song_blueprints = relationship("SongBlueprint", secondary=genre_blueprint_map, back_populates="genres")
    tracks = relationship("Track", secondary=genre_track_map, back_populates="genres")

class Motif(Base):
    __tablename__ = 'motifs'
    id = Column(Integer, primary_key=True)
    motif_name = Column(String(50), nullable=False)             # Name label of current motif
    sequence_data: str = Column(Text, nullable=False)           # type: ignore (Taxonomy Token to classify motifs using their IDs and Enum labels)
    motif_class = Column(Enum(SectionClass), nullable=False)    # Motif classification used to match corresponding blueprint container label
    motif_tag = Column(String(50))                              # Optional sub-classification for heuristic transition grouping
    phrase_latency = Column(Float, nullable=False, default=0.0, server_default="0.0")               # Applies phrase or sequence-level human timing to the motif
    motif_pivot_offset = Column(Float, nullable=False, default=0.0, server_default="0.0")           # "Boundary Line" of a motif, shorter motifs loop until this number is reached, longer motifs are cut off at this point
    rest_duration = Column(Float, nullable=False, default=0.0, server_default="0.0")                # Rest value in beats used for generation logic
    rest_suffix = Column(String(50), nullable=False, default="NONE", server_default="NONE")         # Categorical Metadata tag for SQL switchboard
    created_at = Column(TIMESTAMP, server_default=func.now())       # Log for creation (Upload) timestamp of motif (Allows the DB to handle the timestamp automatically)
    vector_id = Column(String(36), unique=True, nullable=True)      # Unique identifier for corresponding motif vector in Qdrant Vector Database (Used to link SQL records to their respective vectors for generation logic)
    
    notes = relationship("MotifNote", back_populates="motif", cascade="all, delete-orphan")
    stats = relationship("MotifStat", back_populates="motif", cascade="all, delete-orphan", uselist=False)
    tracks = relationship("Track", secondary=track_motif_map, back_populates="motifs")
    outgoing_transitions = relationship("Transition", foreign_keys="[Transition.from_motif_id]", back_populates="from_motif")
    incoming_transitions = relationship("Transition", foreign_keys="[Transition.to_motif_id]", back_populates="to_motif")

class MotifNote(Base):
    __tablename__ = 'motif_notes'
    id = Column(Integer, primary_key=True)
    motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False)
    chord_id = Column(Integer, ForeignKey('chords.id', ondelete="SET NULL"))    # Optional foreign key for chords; defaults to NULL if parent chord is purged from the 'Static Library'
    pitch_value = Column(Integer, nullable=False)   # MIDI value for current motif note
    beat_position = Column(Float, nullable=False)   # Current beat offset of motif note
    duration = Column(Float, nullable=False)        # Duration of motif note
    micro_offset = Column(Float, nullable=False, default=0.0, server_default="0.0")     # Applies note-level human timing

    chord = relationship("Chord", back_populates="motif_notes")
    motif = relationship("Motif", back_populates="notes")

class MotifStat(Base):
    __tablename__ = 'motif_stats'
    id = Column(Integer, primary_key=True)
    motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False, unique=True)
    occurrence_count = Column(Integer, nullable=False, default=0, server_default="0")   # Metadata log for frequency of motif played (To be used in higher-level Markov Chain generation logic)
    last_played = Column(TIMESTAMP, server_default=func.now())                          # Metadata log for timestamp of motif's last usage in the generation of a composition

    motif = relationship("Motif", back_populates="stats")   # Has to be a unique variable due to the relationship being "One-to-One"

class Scale(Base):
    __tablename__ = 'scales'
    id = Column(Integer, primary_key=True)
    scale_name = Column(String(50), nullable=False)         # Name label of current scale
    default_root_note = Column(Integer, nullable=False)     # Default pitch key value of current scale
    intervals = Column(String(50), nullable=False)          # Note semitone interval count for current scale

    tracks = relationship("Track", secondary=track_scale_map, back_populates="scales")

class SongBlueprint(Base):
    __tablename__ = 'song_blueprints'
    id = Column(Integer, primary_key=True)
    block_class = Column(Enum(SectionClass), nullable=False)    # Container label for blueprint block (Used to verify the corresponding eligible motif class using the same Enum)
    block_position = Column(Integer, nullable=False)            # Song structure position for current blueprint block

    genres = relationship("Genre", secondary=genre_blueprint_map, back_populates="song_blueprints")

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    track_name = Column(String(100), nullable=False)            # Name label of current track
    track_class = Column(Enum(TrackClass), nullable=False)      # Structural archetype of current track/instrument (e.g. "Bass", "Melodic Lead")

    midi_channel = Column(Integer, nullable=False, default=1, server_default="1")   # Slot number for current track MIDI channel (NOTE: Drums/Percussion will always occupy the 10th channel per GM standards)
    instrument_name = Column(String(50), nullable=True)         # Metadata label of current track to be processed by MIDI playback engine
    patch_number = Column(Integer, nullable=True)               # Designated value of current track to be processed by MIDI playback engine
    track_motif_limit = Column(Integer, nullable=True)          # Capacity of simultaneous motifs applied to current track

    genres = relationship("Genre", secondary=genre_track_map, back_populates="tracks")
    motifs = relationship("Motif", secondary=track_motif_map, back_populates="tracks")
    scales = relationship("Scale", secondary=track_scale_map, back_populates="tracks")

class Transition(Base):
    __tablename__ = 'transitions'
    id = Column(Integer, primary_key=True)
    from_motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False)    # Designated path for previous motif
    to_motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False)      # Designated path for next motif
    transition_weight = Column(Float, nullable=False)   # Probability of motif being selected as the next harmonic event in Markov Chain

    from_motif = relationship("Motif", foreign_keys=[from_motif_id], back_populates="outgoing_transitions")
    to_motif = relationship("Motif", foreign_keys=[to_motif_id], back_populates="incoming_transitions")
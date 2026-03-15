import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Enum, TIMESTAMP, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

# Motif Class Enum

class BlockClass(enum.Enum):
    OPENING = "Opening"
    VERSE = "Verse"
    PRE_CHORUS = "Pre-Chorus"
    CHORUS = "Chorus"
    BUILD = "Build"
    DE_ESCALATION = "De-Escalation"
    BRIDGE = "Bridge"
    ENTROPIC = "Entropic"
    REST = "Rest"
    OUTRO = "Outro"

class MotifClass(enum.Enum):
    OPENING = "Opening"
    VERSE = "Verse"
    PRE_CHORUS = "Pre-Chorus"
    CHORUS = "Chorus"
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

# 1. The Base: This is what Alembic 'looks' at in your env.py
class Base(DeclarativeBase):
    pass

# 2. The Junction Tables: Handles Many-to-Many (One Motif can have Many Genres)

artist_genre_map = Table(
    'artist_genre_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id', ondelete="CASCADE"), nullable=False),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete="CASCADE"), nullable=False),
    Column('affinity_score', Float) #--- Questionable Column (Needs evaluation) ---
)

genre_blueprint_map = Table(
    'genre_blueprint_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), nullable=False),
    Column('blueprint_id', Integer, ForeignKey('song_blueprints.id'), nullable=False)
)

genre_track_map = Table(
    'genre_track_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), nullable=False),
    Column('track_id', Integer, ForeignKey('tracks.id'), nullable=False),
    Column('selection_weight', Float, nullable=False)
)

track_motif_map = Table(
    'track_motif_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('track_id', Integer, ForeignKey('tracks.id'), nullable=False),
    Column('motif_id', Integer, ForeignKey('motifs.id'), nullable=False),
    Column('selection_weight', Float, nullable=False),
    Column('octave_shift', Integer, nullable=False)
)

track_scale_map = Table(
    'track_scale_map',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('track_id', Integer, ForeignKey('tracks.id'), nullable=False),
    Column('scale_id', Integer, ForeignKey('scales.id'), nullable=False),
    Column('is_default', Boolean, default=False)
)

# The Main Tables

class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    artist_name = Column(String(100), nullable=False)

    genres = relationship("Genre", secondary=artist_genre_map, back_populates="artists")

class Chord(Base):
    __tablename__ = 'chords'
    id = Column(Integer, primary_key=True)
    chord_name = Column(String(28), nullable=False)
    chord_class = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    chord_notes = relationship("ChordNote", back_populates="chord", cascade="all, delete-orphan")
    motif_notes = relationship("MotifNote", back_populates="chord")

class ChordNote(Base):
    __tablename__ = 'chord_notes'
    id = Column(Integer, primary_key=True)
    chord_id = Column(Integer, ForeignKey('chords.id', ondelete="CASCADE"), nullable=False)
    pitch_value = Column(Integer, nullable=False)

    chord = relationship("Chord", back_populates="chord_notes")

class Composition(Base):
    __tablename__ = 'compositions'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now()) # Allows the DB to handle the timestamp automatically

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    genre_name = Column(String(50), unique=True, nullable=False)
    default_tempo = Column(Integer, nullable=False)
    time_signature = Column(String(10), nullable=False)

    artists = relationship("Artist", secondary=artist_genre_map, back_populates="genres")
    song_blueprints = relationship("SongBlueprint", secondary=genre_blueprint_map, back_populates="genres")
    tracks = relationship("Track", secondary=genre_track_map, back_populates="genres")

class Motif(Base):
    __tablename__ = 'motifs'
    id = Column(primary_key=True)
    motif_name = Column(String(50), nullable=False)
    sequence_data: Mapped[str] = mapped_column(Text, nullable=False)
    motif_class = Column(Enum(MotifClass), nullable=False)
    phrase_latency = Column(Float)
    motif_pivot_offset = Column(Float) #--- Questionable Column (Needs evaluation) ---
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    notes = relationship("MotifNote", back_populates="motifs", cascade="all, delete-orphan")
    stats = relationship("MotifStat", back_populates="motif", cascade="all, delete-orphan", uselist=False)
    tracks = relationship("Track", secondary=track_motif_map, back_populates="motifs")
    outgoing_transitions = relationship("Transition", foreign_keys="[Transition.from_motif_id]", back_populates="from_motif")
    incoming_transitions = relationship("Transition", foreign_keys="[Transition.to_motif_id]", back_populates="to_motif")

class MotifNote(Base):
    __tablename__ = 'motif_notes'
    id = Column(Integer, primary_key=True)
    motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False)
    chord_id = Column(Integer, ForeignKey('chords.id'))
    pitch_value = Column(Integer, nullable=False)
    beat_position = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    micro_offset = Column(Float)

    chord = relationship("Chord", back_populates="motif_notes")

class MotifStat(Base):
    __tablename__ = 'motif_stats'
    id = Column(Integer, primary_key=True)
    motif_id = Column(Integer, ForeignKey('motifs.id', ondelete="CASCADE"), nullable=False)
    occurence_count = Column(Integer, default=0)
    last_played = Column(TIMESTAMP, server_default=func.now())

    motif = relationship("Motif", back_populates="stats") # Has to be a unique variable due to the relationship being "One-to-One"

class Scale(Base):
    __tablename__ = 'scales'
    id = Column(Integer, primary_key=True)
    scale_name = Column(String(50), nullable=False)
    default_root_note = Column(Integer, nullable=False)
    intervals = Column(String(50), nullable=False)

    tracks = relationship("Track", secondary=track_scale_map, back_populates="scales")

class SongBlueprint(Base):
    __tablename__ = 'song_blueprints'
    id = Column(Integer, primary_key=True)
    block_class = Column(Enum(BlockClass), nullable=False)
    block_position = Column(Integer, nullable=False)

    genres = relationship("Genre", secondary=genre_blueprint_map, back_populates="song_blueprints")

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    track_name = Column(String(100), nullable=False)
    track_class = Column(Enum(TrackClass), nullable=False)

    genres = relationship("Genre", secondary=genre_track_map, back_populates="tracks")
    motifs = relationship("Motif", secondary=track_motif_map, back_populates="tracks")
    scales = relationship("Scale", secondary=track_scale_map, back_populates="tracks")

class Transition(Base):
    __tablename__ = 'transitions'
    id = Column(Integer, primary_key=True)
    from_motif_id = Column(Integer, ForeignKey('motifs.id'), nullable=False)
    to_motif_id = Column(Integer, ForeignKey('motifs.id'), nullable=False)
    transition_weight = Column(Float, nullable=False)

    from_motif = relationship("Motif", foreign_keys=[from_motif_id], back_populates="outgoing_transitions")
    to_motif = relationship("Motif", foreign_keys=[to_motif_id], back_populates="incoming_transitions")

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(50), nullable=False)
    setting_value = Column(String(100), nullable=False)
"""Match-related models for cricket matches."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Match(Base):
    """Cricket match model with ULID-based public IDs."""
    
    __tablename__ = "matches"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Foreign keys
    tournament_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tournaments.id"),
        doc="Reference to tournament (optional for bilateral series)"
    )
    venue_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("venues.id"),
        nullable=False,
        doc="Reference to venue where match is played"
    )
    
    # Match details
    match_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="Type of cricket match (T20, ODI, TEST, T10, 100BALL)"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="Match status (SCHEDULED, LIVE, COMPLETED, ABANDONED, CANCELLED)"
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Scheduled start time in UTC"
    )
    local_tz: Mapped[Optional[str]] = mapped_column(
        String(64),
        doc="Local timezone at venue"
    )
    overs_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Overs per innings (NULL for unlimited/TEST matches)"
    )
    balls_per_over: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of balls per over (typically 6)"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional notes or comments about the match"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    tournament: Mapped[Optional["Tournament"]] = relationship(
        "Tournament",
        back_populates="matches",
        doc="Tournament this match belongs to"
    )
    venue: Mapped["Venue"] = relationship(
        "Venue",
        back_populates="matches",
        doc="Venue where match is played"
    )
    teams: Mapped[list["MatchTeam"]] = relationship(
        "MatchTeam",
        back_populates="match",
        cascade="all, delete-orphan",
        doc="Teams participating in this match"
    )
    toss: Mapped[Optional["MatchToss"]] = relationship(
        "MatchToss",
        back_populates="match",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Toss information for this match"
    )
    match_players: Mapped[list["MatchPlayer"]] = relationship(
        "MatchPlayer",
        back_populates="match",
        cascade="all, delete-orphan",
        doc="Players participating in this match"
    )
    innings: Mapped[list["Innings"]] = relationship(
        "Innings",
        back_populates="match",
        cascade="all, delete-orphan",
        doc="All innings in this match"
    )
    
    def __init__(self, **kwargs):
        """Initialize match with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(new_ulid())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
        return {
            "public_id": self.public_id,
            "tournament_id": self.tournament_id,
            "venue_id": self.venue_id,
            "match_type": self.match_type,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "local_tz": self.local_tz,
            "overs_limit": self.overs_limit,
            "balls_per_over": self.balls_per_over,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Match(id={self.public_id}, type={self.match_type}, status={self.status})>"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.match_type} Match at {self.venue.name if hasattr(self, 'venue') and self.venue else 'TBD'}"


class MatchTeam(Base):
    """Association model for Match-Team relationship."""
    
    __tablename__ = "match_team"
    __table_args__ = (
        UniqueConstraint('match_id', 'team_id', name='uq_match_team'),
    )
    
    # Foreign keys
    match_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the match"
    )
    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        doc="Reference to the team"
    )
    
    # Additional fields
    is_home: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this team is the home team"
    )
    
    # Relationships
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="teams",
        doc="Match this association refers to"
    )
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="matches",
        doc="Team this association refers to"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<MatchTeam(match_id={self.match_id}, team_id={self.team_id}, is_home={self.is_home})>"


class MatchToss(Base):
    """Match toss information."""
    
    __tablename__ = "match_toss"
    
    # The match_id is the primary key (one-to-one with Match)
    match_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("matches.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Reference to the match"
    )
    
    # Foreign key
    won_by_team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        doc="Team that won the toss"
    )
    
    # Toss decision
    decision: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        doc="Toss decision: BAT or BOWL"
    )
    
    # Relationships
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="toss",
        doc="Match this toss belongs to"
    )
    team: Mapped["Team"] = relationship(
        "Team",
        doc="Team that won the toss"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<MatchToss(match_id={self.match_id}, won_by_team_id={self.won_by_team_id}, decision={self.decision})>"

"""Innings model - represents an innings in a cricket match."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Innings(Base):
    """
    Innings model representing a single innings in a cricket match.
    
    An innings is when one team bats. In limited overs cricket (T20, ODI)
    each team typically has one innings. In Test cricket, teams can have
    two innings each.
    
    Tracks:
    - Which teams are batting and bowling
    - Innings sequence number in the match
    - Special situations: follow-on, declarations, forfeits
    - Target runs (for chasing team)
    """
    
    __tablename__ = "innings"
    
    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Public ID (ULID)
    public_id: Mapped[str] = mapped_column(
        String(26),
        unique=True,
        nullable=False,
        default=lambda: str(new_ulid()),
        doc="Public-facing ULID identifier"
    )
    
    # Foreign Keys
    match_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        doc="Match this innings belongs to"
    )
    batting_team_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teams.id"),
        nullable=False,
        doc="Team that is batting in this innings"
    )
    bowling_team_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teams.id"),
        nullable=False,
        doc="Team that is bowling in this innings"
    )
    
    # Innings Information
    seq_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Innings number in the match (1, 2, 3, 4 for Test matches)"
    )
    
    # Special Situations (Test cricket)
    follow_on: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this innings is a follow-on (Test cricket)"
    )
    declared: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the batting team declared this innings"
    )
    forfeited: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the batting team forfeited this innings"
    )
    
    # Target Information
    target_runs: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Target runs for this innings (for chasing team)"
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
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("match_id", "seq_number", name="uq_innings_match_seq"),
    )
    
    # Relationships
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="innings",
        doc="Match this innings belongs to"
    )
    batting_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[batting_team_id],
        doc="Team batting in this innings"
    )
    bowling_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[bowling_team_id],
        doc="Team bowling in this innings"
    )
    deliveries: Mapped[list["Delivery"]] = relationship(
        "Delivery",
        back_populates="innings",
        doc="All deliveries in this innings"
    )
    
    def __init__(self, **kwargs):
        """Initialize an Innings instance."""
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert the Innings instance to a dictionary."""
        return {
            "id": self.id,
            "public_id": self.public_id,
            "match_id": self.match_id,
            "seq_number": self.seq_number,
            "batting_team_id": self.batting_team_id,
            "bowling_team_id": self.bowling_team_id,
            "follow_on": self.follow_on,
            "declared": self.declared,
            "forfeited": self.forfeited,
            "target_runs": self.target_runs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __str__(self) -> str:
        """String representation of the Innings."""
        status = []
        if self.follow_on:
            status.append("follow-on")
        if self.declared:
            status.append("declared")
        if self.forfeited:
            status.append("forfeited")
        
        status_str = f" ({', '.join(status)})" if status else ""
        target_str = f" - Target: {self.target_runs}" if self.target_runs else ""
        
        return f"Innings #{self.seq_number} (Match #{self.match_id}){status_str}{target_str}"
    
    def __repr__(self) -> str:
        """Developer representation of the Innings."""
        return (
            f"<Innings(id={self.id}, public_id={self.public_id}, "
            f"match_id={self.match_id}, seq_number={self.seq_number})>"
        )

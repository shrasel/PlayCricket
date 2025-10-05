"""Delivery model - ball-by-ball tracking for cricket matches."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, Float, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Delivery(Base):
    """
    Delivery model representing a single ball bowled in a cricket match.
    
    This is the most granular level of cricket data, tracking every ball
    bowled including:
    - Who bowled it and who faced it
    - Runs scored (by batter and extras)
    - Boundaries (fours and sixes)
    - Wickets (type, who got out, fielder involved)
    - Ball position data (wagon wheel and pitch maps)
    - Commentary
    - Corrections/replacements
    """
    
    __tablename__ = "delivery"
    
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
    innings_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("innings.id", ondelete="CASCADE"),
        nullable=False,
        doc="Innings this delivery belongs to"
    )
    striker_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
        doc="Batter facing this delivery"
    )
    non_striker_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
        doc="Batter at non-striker end"
    )
    bowler_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
        doc="Bowler delivering this ball"
    )
    
    # Delivery Position in Innings
    over_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Over number (0-based or 1-based depending on convention)"
    )
    ball_in_over: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Ball number within the over (1-6 normally, can be higher with extras)"
    )
    
    # Delivery Type
    is_legal_delivery: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Whether this is a legal delivery (False for wides, no-balls)"
    )
    
    # Timestamp
    ts_utc: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Timestamp when delivery was bowled (ISO format)"
    )
    
    # Runs Scored
    runs_batter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Runs scored by the batter off this delivery"
    )
    runs_extras: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Extra runs conceded (wides, no-balls, byes, leg-byes)"
    )
    
    # Extras Information
    extra_type: Mapped[Optional[str]] = mapped_column(
        String(16),
        nullable=True,
        doc="Type of extra: WIDE, NO_BALL, BYE, LEG_BYE, PENALTY"
    )
    
    # Boundaries
    is_four: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this delivery resulted in a four"
    )
    is_six: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this delivery resulted in a six"
    )
    
    # Wicket Information
    wicket_type: Mapped[Optional[str]] = mapped_column(
        String(16),
        nullable=True,
        doc="Type of wicket: BOWLED, CAUGHT, LBW, RUN_OUT, STUMPED, etc."
    )
    out_player_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=True,
        doc="Player who got out (if wicket fell)"
    )
    fielder_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=True,
        doc="Fielder involved in dismissal (if applicable)"
    )
    
    # Shot/Ball Tracking Coordinates
    wagon_x: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Wagon wheel X coordinate (0-100 normalized)"
    )
    wagon_y: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Wagon wheel Y coordinate (0-100 normalized)"
    )
    pitch_x: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Pitch map X coordinate for ball landing position"
    )
    pitch_y: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Pitch map Y coordinate for ball landing position"
    )
    
    # Commentary
    commentary_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Ball-by-ball commentary text"
    )
    
    # Correction/Replacement
    replaces_delivery_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("delivery.id"),
        nullable=True,
        doc="If this delivery corrects/replaces another, reference to original"
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
    
    # Constraints and Indexes
    __table_args__ = (
        # Unique constraint: each ball in an innings is unique
        # COALESCE handles null replaces_delivery_id
        UniqueConstraint(
            "innings_id", "over_number", "ball_in_over", 
            "replaces_delivery_id",
            name="uq_delivery_innings_ball"
        ),
        # Index for efficient innings/over queries
        Index("idx_delivery_innings_over", "innings_id", "over_number"),
        # Index for bowler statistics
        Index("idx_delivery_bowler", "bowler_id"),
        # Index for batter statistics
        Index("idx_delivery_batters", "striker_id", "non_striker_id"),
    )
    
    # Relationships
    innings: Mapped["Innings"] = relationship(
        "Innings",
        back_populates="deliveries",
        doc="Innings this delivery belongs to"
    )
    striker: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[striker_id],
        doc="Batter facing the delivery"
    )
    non_striker: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[non_striker_id],
        doc="Batter at non-striker end"
    )
    bowler: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[bowler_id],
        doc="Bowler delivering the ball"
    )
    out_player: Mapped[Optional["Player"]] = relationship(
        "Player",
        foreign_keys=[out_player_id],
        doc="Player who got out (if applicable)"
    )
    fielder: Mapped[Optional["Player"]] = relationship(
        "Player",
        foreign_keys=[fielder_id],
        doc="Fielder involved in dismissal (if applicable)"
    )
    
    def __init__(self, **kwargs):
        """Initialize a Delivery instance."""
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert the Delivery instance to a dictionary."""
        return {
            "id": self.id,
            "public_id": self.public_id,
            "innings_id": self.innings_id,
            "over_number": self.over_number,
            "ball_in_over": self.ball_in_over,
            "is_legal_delivery": self.is_legal_delivery,
            "ts_utc": self.ts_utc,
            "striker_id": self.striker_id,
            "non_striker_id": self.non_striker_id,
            "bowler_id": self.bowler_id,
            "runs_batter": self.runs_batter,
            "runs_extras": self.runs_extras,
            "extra_type": self.extra_type,
            "is_four": self.is_four,
            "is_six": self.is_six,
            "wicket_type": self.wicket_type,
            "out_player_id": self.out_player_id,
            "fielder_id": self.fielder_id,
            "wagon_x": self.wagon_x,
            "wagon_y": self.wagon_y,
            "pitch_x": self.pitch_x,
            "pitch_y": self.pitch_y,
            "commentary_text": self.commentary_text,
            "replaces_delivery_id": self.replaces_delivery_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __str__(self) -> str:
        """String representation of the Delivery."""
        runs = self.runs_batter + self.runs_extras
        
        details = []
        if self.is_four:
            details.append("FOUR")
        elif self.is_six:
            details.append("SIX")
        elif self.wicket_type:
            details.append(f"WICKET ({self.wicket_type})")
        elif self.extra_type:
            details.append(self.extra_type)
        
        details_str = f" - {', '.join(details)}" if details else ""
        
        return f"{self.over_number}.{self.ball_in_over}: {runs} run{'s' if runs != 1 else ''}{details_str}"
    
    def __repr__(self) -> str:
        """Developer representation of the Delivery."""
        return (
            f"<Delivery(id={self.id}, innings_id={self.innings_id}, "
            f"over={self.over_number}.{self.ball_in_over}, "
            f"runs={self.runs_batter}+{self.runs_extras})>"
        )

"""Player model for cricket players."""
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Player(Base):
    """Cricket player model with ULID-based public IDs."""
    
    __tablename__ = "players"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Player details
    full_name: Mapped[str] = mapped_column(
        String(160), 
        nullable=False,
        doc="Full legal name of the player"
    )
    known_as: Mapped[Optional[str]] = mapped_column(
        String(80),
        doc="Nickname or preferred name (e.g., 'MS Dhoni')"
    )
    dob: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date of birth"
    )
    
    # Playing style
    batting_style: Mapped[Optional[str]] = mapped_column(
        String(8),
        doc="Batting style: RHB (Right-hand bat) or LHB (Left-hand bat)"
    )
    bowling_style: Mapped[Optional[str]] = mapped_column(
        String(64),
        doc="Bowling style description (e.g., 'Right-arm fast', 'Left-arm orthodox')"
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
    teams: Mapped[list["TeamPlayer"]] = relationship(
        "TeamPlayer",
        back_populates="player",
        doc="Teams this player has been associated with"
    )
    
    def __init__(self, **kwargs):
        """Initialize player with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(new_ulid())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
        return {
            "public_id": self.public_id,
            "full_name": self.full_name,
            "known_as": self.known_as,
            "dob": self.dob.isoformat() if self.dob else None,
            "batting_style": self.batting_style,
            "bowling_style": self.bowling_style,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_age(self, reference_date: Optional[date] = None) -> Optional[int]:
        """
        Calculate player's age.
        
        Args:
            reference_date: Date to calculate age from (defaults to today)
            
        Returns:
            Age in years, or None if DOB not available
        """
        if not self.dob:
            return None
            
        if reference_date is None:
            reference_date = date.today()
            
        age = reference_date.year - self.dob.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (reference_date.month, reference_date.day) < (self.dob.month, self.dob.day):
            age -= 1
            
        return age
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Player(id={self.public_id}, name={self.full_name})>"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.known_as if self.known_as else self.full_name

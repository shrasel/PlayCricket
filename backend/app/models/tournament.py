"""Tournament model for cricket tournaments and leagues."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Tournament(Base):
    """Cricket tournament model with ULID-based public IDs."""
    
    __tablename__ = "tournaments"
    __table_args__ = (
        UniqueConstraint('name', 'season_label', name='uq_tournament_name_season'),
    )
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Tournament details
    name: Mapped[str] = mapped_column(
        String(160), 
        nullable=False,
        doc="Full name of the tournament (e.g., 'Indian Premier League', 'ICC World Cup')"
    )
    season_label: Mapped[Optional[str]] = mapped_column(
        String(32),
        doc="Season or year identifier (e.g., '2024', '2023-24')"
    )
    match_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="Type of cricket match (T20, ODI, TEST, T10, 100BALL)"
    )
    points_system: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        doc="Points allocation system as JSON (e.g., {win: 2, loss: 0, tie: 1})"
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
    matches: Mapped[list["Match"]] = relationship(
        "Match",
        back_populates="tournament",
        doc="Matches in this tournament"
    )
    
    def __init__(self, **kwargs):
        """Initialize tournament with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(new_ulid())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
        return {
            "public_id": self.public_id,
            "name": self.name,
            "season_label": self.season_label,
            "match_type": self.match_type,
            "points_system": self.points_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Tournament(id={self.public_id}, name={self.name})>"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.season_label:
            return f"{self.name} {self.season_label}"
        return self.name

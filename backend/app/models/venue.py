"""Venue model for cricket grounds and stadiums."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Venue(Base):
    """Cricket venue/stadium model with ULID-based public IDs."""
    
    __tablename__ = "venues"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Venue details
    name: Mapped[str] = mapped_column(
        String(160), 
        unique=True,
        nullable=False,
        doc="Full name of the cricket ground/stadium"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(80),
        doc="City where the venue is located"
    )
    country_code: Mapped[Optional[str]] = mapped_column(
        String(3),
        doc="ISO 3166-1 alpha-3 country code (e.g., 'IND', 'AUS', 'ENG')"
    )
    timezone_name: Mapped[Optional[str]] = mapped_column(
        String(64),
        doc="IANA timezone identifier (e.g., 'Asia/Kolkata', 'Australia/Sydney')"
    )
    ends_names: Mapped[Optional[str]] = mapped_column(
        String(160),
        doc="Names of the two ends of the ground (e.g., 'Pavilion End, Nursery End')"
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
        back_populates="venue",
        doc="Matches played at this venue"
    )
    
    def __init__(self, **kwargs):
        """Initialize venue with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(new_ulid())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
        return {
            "public_id": self.public_id,
            "name": self.name,
            "city": self.city,
            "country_code": self.country_code,
            "timezone_name": self.timezone_name,
            "ends_names": self.ends_names,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Venue(id={self.public_id}, name={self.name})>"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.city:
            return f"{self.name}, {self.city}"
        return self.name

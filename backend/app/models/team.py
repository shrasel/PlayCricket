"""Team model for cricket teams."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ulid import new as new_ulid
from app.models.base import Base


class Team(Base):
    """Cricket team model with ULID-based public IDs."""
    
    __tablename__ = "teams"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Team details
    name: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        doc="Full team name"
    )
    short_name: Mapped[str] = mapped_column(
        String(10), 
        unique=True, 
        nullable=False,
        doc="Abbreviated team name (e.g., 'IND', 'AUS')"
    )
    country_code: Mapped[Optional[str]] = mapped_column(
        String(3),
        doc="ISO 3166-1 alpha-3 country code (e.g., 'IND', 'AUS')"
    )
    primary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Primary team color (hex format #RRGGBB)"
    )
    secondary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Secondary team color (hex format #RRGGBB)"
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="URL to team logo image"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    players: Mapped[list["TeamPlayer"]] = relationship(
        "TeamPlayer",
        back_populates="team",
        doc="Players associated with this team"
    )
    matches: Mapped[list["MatchTeam"]] = relationship(
        "MatchTeam",
        back_populates="team",
        doc="Matches this team has participated in"
    )
    
    def __init__(self, **kwargs):
        """Initialize team with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(new_ulid())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
        return {
            "public_id": self.public_id,
            "name": self.name,
            "short_name": self.short_name,
            "country_code": self.country_code,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "logo_url": self.logo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Team(id={self.public_id}, name={self.name})>"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.name} ({self.short_name})"

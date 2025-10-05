"""TeamPlayer association model for team-player relationships."""
from datetime import date
from typing import Optional
from sqlalchemy import Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class TeamPlayer(Base):
    """Association model for Team-Player many-to-many relationship."""
    
    __tablename__ = "team_player"
    
    # Foreign keys
    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the team"
    )
    player_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to the player"
    )
    
    # Additional fields
    shirt_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Player's jersey/shirt number for this team"
    )
    role_hint_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Hint about player's primary role (batsman, bowler, all-rounder, wicket-keeper)"
    )
    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when player joined the team"
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        doc="Date when player left the team (NULL if still active)"
    )
    
    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="players",
        doc="Team this association refers to"
    )
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="teams",
        doc="Player this association refers to"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<TeamPlayer(team_id={self.team_id}, player_id={self.player_id})>"

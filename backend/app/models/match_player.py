"""MatchPlayer model - links players to specific matches."""
from typing import Optional
from sqlalchemy import Integer, BigInteger, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class MatchPlayer(Base):
    """
    MatchPlayer model representing a player's participation in a specific match.
    
    Tracks:
    - Which players were in the playing XI
    - Captain and wicketkeeper designations
    - Batting order
    - Substitute players
    """
    
    __tablename__ = "match_player"
    
    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    match_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        doc="Match this player is participating in"
    )
    team_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teams.id"),
        nullable=False,
        doc="Team the player is representing"
    )
    player_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("players.id"),
        nullable=False,
        doc="Player participating in the match"
    )
    
    # Player Status Fields
    is_playing_xi: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether player is in the starting XI (False for substitutes)"
    )
    is_captain: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether player is the team captain"
    )
    is_wicketkeeper: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether player is the wicketkeeper"
    )
    
    # Optional Fields
    batting_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Batting order position (if applicable)"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_match_player"),
    )
    
    # Relationships
    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="match_players",
        doc="Match this player is participating in"
    )
    team: Mapped["Team"] = relationship(
        "Team",
        doc="Team the player is representing"
    )
    player: Mapped["Player"] = relationship(
        "Player",
        doc="Player details"
    )
    
    def __init__(self, **kwargs):
        """Initialize a MatchPlayer instance."""
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert the MatchPlayer instance to a dictionary."""
        return {
            "id": self.id,
            "match_id": self.match_id,
            "team_id": self.team_id,
            "player_id": self.player_id,
            "is_playing_xi": self.is_playing_xi,
            "is_captain": self.is_captain,
            "is_wicketkeeper": self.is_wicketkeeper,
            "batting_order": self.batting_order,
        }
    
    def __str__(self) -> str:
        """String representation of the MatchPlayer."""
        role = []
        if self.is_captain:
            role.append("Captain")
        if self.is_wicketkeeper:
            role.append("WK")
        if not self.is_playing_xi:
            role.append("Substitute")
        
        role_str = f" ({', '.join(role)})" if role else ""
        batting_str = f" - #{self.batting_order}" if self.batting_order else ""
        
        return f"MatchPlayer(Match#{self.match_id}, Player#{self.player_id}{role_str}{batting_str})"
    
    def __repr__(self) -> str:
        """Developer representation of the MatchPlayer."""
        return (
            f"<MatchPlayer(id={self.id}, match_id={self.match_id}, "
            f"player_id={self.player_id}, team_id={self.team_id}, "
            f"is_playing_xi={self.is_playing_xi}, is_captain={self.is_captain})>"
        )

"""Match schemas for API requests and responses."""
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas import TimestampMixin, PublicIdMixin
from app.schemas.team import TeamSummary
from app.schemas.venue import VenueSummary
from app.schemas.tournament import TournamentSummary


class MatchTeamBase(BaseModel):
    """Base schema for match-team association."""
    team_id: str = Field(..., description="Team public ULID")
    is_home: bool = Field(False, description="Whether this team is playing at home")


class MatchTossBase(BaseModel):
    """Base schema for match toss."""
    toss_winner_id: str = Field(..., description="Team public ULID of toss winner")
    elected_to: str = Field(..., description="BAT or BOWL")


class MatchBase(BaseModel):
    """Base match schema with common fields."""
    venue_id: str = Field(..., description="Venue public ULID")
    tournament_id: Optional[str] = Field(None, description="Tournament public ULID")
    match_type: str = Field(..., max_length=20, description="T20, ODI, TEST, T10, 100BALL")
    status: str = Field("SCHEDULED", max_length=20, description="SCHEDULED, LIVE, COMPLETED, ABANDONED, CANCELLED")
    start_time: Optional[datetime] = Field(None, description="Scheduled start time (UTC)")
    local_tz: Optional[str] = Field(None, max_length=64, description="Local timezone at venue")
    overs_limit: Optional[int] = Field(None, ge=1, description="Overs per innings (NULL for unlimited/TEST)")
    balls_per_over: int = Field(6, ge=1, le=10, description="Number of balls per over (typically 6)")
    notes: Optional[str] = Field(None, description="Additional notes or comments about the match")


class MatchCreate(MatchBase):
    """Schema for creating a new match."""
    teams: List[MatchTeamBase] = Field(..., min_items=2, max_items=2, description="Two teams")
    toss: Optional[MatchTossBase] = Field(None, description="Toss details (optional at creation)")


class MatchUpdate(BaseModel):
    """Schema for updating a match (all fields optional)."""
    venue_id: Optional[str] = None
    tournament_id: Optional[str] = None
    match_type: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    start_time: Optional[datetime] = None
    local_tz: Optional[str] = Field(None, max_length=64)
    overs_limit: Optional[int] = Field(None, ge=1)
    balls_per_over: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class MatchTossUpdate(BaseModel):
    """Schema for updating match toss."""
    toss_winner_id: str = Field(..., description="Team public ULID of toss winner")
    elected_to: str = Field(..., description="BAT or BOWL")


class MatchInDB(MatchBase, PublicIdMixin, TimestampMixin):
    """Match schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class MatchResponse(PublicIdMixin, TimestampMixin):
    """Match schema for API responses with nested relationships."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")
    match_type: str = Field(..., max_length=20, description="T20, ODI, TEST, T10, 100BALL")
    status: str = Field("SCHEDULED", max_length=20, description="SCHEDULED, LIVE, COMPLETED, ABANDONED, CANCELLED")
    start_time: Optional[datetime] = Field(None, description="Scheduled start time (UTC)")
    local_tz: Optional[str] = Field(None, max_length=64, description="Local timezone at venue")
    overs_limit: Optional[int] = Field(None, ge=1, description="Overs per innings (NULL for unlimited/TEST)")
    balls_per_over: int = Field(6, ge=1, le=10, description="Number of balls per over (typically 6)")
    notes: Optional[str] = Field(None, description="Additional notes or comments about the match")
    venue: Optional[VenueSummary] = None
    tournament: Optional[TournamentSummary] = None
    teams: List[TeamSummary] = Field(default_factory=list, description="Participating teams")
    
    @field_validator('teams', mode='before')
    @classmethod
    def extract_teams_from_match_teams(cls, v):
        """Extract Team objects from MatchTeam associations."""
        if not v:
            return []
        # If it's already a list of Team/TeamSummary, return as-is
        if isinstance(v, list) and len(v) > 0:
            # Check if it's MatchTeam objects (they have a 'team' attribute)
            if hasattr(v[0], 'team'):
                return [mt.team for mt in v]
        return v


class MatchSummary(BaseModel):
    """Lightweight match summary for nested responses."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    match_type: str = Field(..., description="Match type")
    status: str = Field(..., description="Match status")
    start_time: Optional[datetime] = Field(None, description="Scheduled start time")
    venue: Optional[VenueSummary] = None
    teams: List[TeamSummary] = Field(default_factory=list, description="Participating teams")
    
    @field_validator('teams', mode='before')
    @classmethod
    def extract_teams_from_match_teams(cls, v):
        """Extract Team objects from MatchTeam associations."""
        if not v:
            return []
        # If it's already a list of Team/TeamSummary, return as-is
        if isinstance(v, list) and len(v) > 0:
            # Check if it's MatchTeam objects (they have a 'team' attribute)
            if hasattr(v[0], 'team'):
                return [mt.team for mt in v]
        return v

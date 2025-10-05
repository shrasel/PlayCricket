"""Match schemas for API requests and responses."""
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field

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
    match_number: Optional[str] = Field(None, max_length=50, description="Match number in tournament")
    match_type: str = Field(..., max_length=20, description="T20, ODI, TEST, T10, 100BALL")
    status: str = Field("SCHEDULED", max_length=20, description="SCHEDULED, LIVE, COMPLETED, ABANDONED, CANCELLED")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time (UTC)")
    actual_start: Optional[datetime] = Field(None, description="Actual start time (UTC)")
    end_time: Optional[datetime] = Field(None, description="Match end time (UTC)")
    overs_per_innings: Optional[int] = Field(None, ge=1, description="Overs per innings")
    is_day_night: bool = Field(False, description="Day-night match flag")
    is_neutral_venue: bool = Field(False, description="Neutral venue flag")
    result_type: Optional[str] = Field(None, max_length=50, description="NORMAL, TIE, NO_RESULT, SUPER_OVER")
    winning_team_id: Optional[str] = Field(None, description="Winning team public ULID")
    result_margin: Optional[str] = Field(None, max_length=100, description="Win margin description")


class MatchCreate(MatchBase):
    """Schema for creating a new match."""
    teams: List[MatchTeamBase] = Field(..., min_items=2, max_items=2, description="Two teams")
    toss: Optional[MatchTossBase] = Field(None, description="Toss details (optional at creation)")


class MatchUpdate(BaseModel):
    """Schema for updating a match (all fields optional)."""
    venue_id: Optional[str] = None
    tournament_id: Optional[str] = None
    match_number: Optional[str] = Field(None, max_length=50)
    match_type: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    end_time: Optional[datetime] = None
    overs_per_innings: Optional[int] = Field(None, ge=1)
    is_day_night: Optional[bool] = None
    is_neutral_venue: Optional[bool] = None
    result_type: Optional[str] = Field(None, max_length=50)
    winning_team_id: Optional[str] = None
    result_margin: Optional[str] = Field(None, max_length=100)


class MatchTossUpdate(BaseModel):
    """Schema for updating match toss."""
    toss_winner_id: str = Field(..., description="Team public ULID of toss winner")
    elected_to: str = Field(..., description="BAT or BOWL")


class MatchInDB(MatchBase, PublicIdMixin, TimestampMixin):
    """Match schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class MatchResponse(MatchInDB):
    """Match schema for API responses with nested relationships."""
    venue: Optional[VenueSummary] = None
    tournament: Optional[TournamentSummary] = None
    teams: List[TeamSummary] = Field(default_factory=list, description="Participating teams")
    toss_winner: Optional[TeamSummary] = None
    winning_team: Optional[TeamSummary] = None


class MatchSummary(BaseModel):
    """Lightweight match summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    match_type: str = Field(..., description="Match type")
    status: str = Field(..., description="Match status")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    venue: Optional[VenueSummary] = None
    teams: List[TeamSummary] = Field(default_factory=list, description="Participating teams")

"""Innings schemas for API requests and responses."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas import TimestampMixin, PublicIdMixin
from app.schemas.team import TeamSummary


class InningsBase(BaseModel):
    """Base innings schema with common fields."""
    match_id: str = Field(..., description="Match public ULID")
    seq_number: int = Field(..., ge=1, description="Innings sequence number (1, 2, 3, 4 for Test)")
    batting_team_id: str = Field(..., description="Batting team public ULID")
    bowling_team_id: str = Field(..., description="Bowling team public ULID")
    follow_on: bool = Field(False, description="Follow-on flag (Test cricket)")
    declared: bool = Field(False, description="Declared innings flag (Test cricket)")
    forfeited: bool = Field(False, description="Forfeited innings flag")
    target_runs: Optional[int] = Field(None, ge=0, description="Target runs (for 2nd/4th innings)")


class InningsCreate(InningsBase):
    """Schema for creating a new innings."""
    pass


class InningsUpdate(BaseModel):
    """Schema for updating an innings (all fields optional)."""
    seq_number: Optional[int] = Field(None, ge=1)
    batting_team_id: Optional[str] = None
    bowling_team_id: Optional[str] = None
    follow_on: Optional[bool] = None
    declared: Optional[bool] = None
    forfeited: Optional[bool] = None
    target_runs: Optional[int] = Field(None, ge=0)


class InningsInDB(InningsBase, PublicIdMixin, TimestampMixin):
    """Innings schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class InningsResponse(InningsInDB):
    """Innings schema for API responses with nested relationships."""
    batting_team: Optional[TeamSummary] = None
    bowling_team: Optional[TeamSummary] = None
    # Calculated fields (computed from deliveries)
    total_runs: int = Field(0, description="Total runs scored")
    total_wickets: int = Field(0, description="Total wickets fallen")
    total_overs: float = Field(0.0, description="Total overs bowled")
    is_all_out: bool = Field(False, description="All out flag")


class InningsSummary(BaseModel):
    """Lightweight innings summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    seq_number: int = Field(..., description="Innings sequence number")
    batting_team: Optional[TeamSummary] = None
    total_runs: int = Field(0, description="Total runs scored")
    total_wickets: int = Field(0, description="Total wickets fallen")
    total_overs: float = Field(0.0, description="Total overs bowled")

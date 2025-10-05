"""Tournament schemas for API requests and responses."""
from typing import Optional, Any, Dict
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, validator

from app.schemas import TimestampMixin, PublicIdMixin


class TournamentBase(BaseModel):
    """Base tournament schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Tournament name")
    short_name: Optional[str] = Field(None, max_length=50, description="Abbreviated name")
    season: Optional[str] = Field(None, max_length=20, description="Season identifier (e.g., '2024', '2023/24')")
    match_type: Optional[str] = Field(None, max_length=20, description="Match type: T20, ODI, TEST, T10, 100BALL")
    start_date: Optional[date] = Field(None, description="Tournament start date")
    end_date: Optional[date] = Field(None, description="Tournament end date")
    points_system: Optional[Dict[str, Any]] = Field(
        None, 
        description="JSON object defining points system: {win: 2, loss: 0, tie: 1, no_result: 1, bonus_point_rules: {...}}"
    )
    
    @validator('points_system')
    def validate_points_system(cls, v):
        """Validate points_system JSON structure."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('points_system must be a JSON object')
        return v


class TournamentCreate(TournamentBase):
    """Schema for creating a new tournament."""
    pass


class TournamentUpdate(BaseModel):
    """Schema for updating a tournament (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)
    season: Optional[str] = Field(None, max_length=20)
    match_type: Optional[str] = Field(None, max_length=20)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    points_system: Optional[Dict[str, Any]] = None
    
    @validator('points_system')
    def validate_points_system(cls, v):
        """Validate points_system JSON structure."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('points_system must be a JSON object')
        return v


class TournamentInDB(TournamentBase, PublicIdMixin, TimestampMixin):
    """Tournament schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class TournamentResponse(TournamentInDB):
    """Tournament schema for API responses."""
    pass


class TournamentSummary(BaseModel):
    """Lightweight tournament summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    name: str = Field(..., description="Tournament name")
    short_name: Optional[str] = Field(None, description="Abbreviated name")
    season: Optional[str] = Field(None, description="Season identifier")
    match_type: Optional[str] = Field(None, description="Match type")

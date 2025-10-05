"""Player schemas for API requests and responses."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas import TimestampMixin, PublicIdMixin


class PlayerBase(BaseModel):
    """Base player schema with common fields."""
    full_name: str = Field(..., min_length=1, max_length=100, description="Player's full name")
    known_as: Optional[str] = Field(None, max_length=100, description="Player's preferred/known name")
    dob: Optional[date] = Field(None, description="Date of birth")
    batting_style: Optional[str] = Field(None, max_length=20, description="Batting style (RHB, LHB)")
    bowling_style: Optional[str] = Field(None, max_length=50, description="Bowling style")


class PlayerCreate(PlayerBase):
    """Schema for creating a new player."""
    pass


class PlayerUpdate(BaseModel):
    """Schema for updating a player (all fields optional)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    known_as: Optional[str] = Field(None, max_length=100)
    dob: Optional[date] = None
    batting_style: Optional[str] = Field(None, max_length=20)
    bowling_style: Optional[str] = Field(None, max_length=50)


class PlayerInDB(PlayerBase, PublicIdMixin, TimestampMixin):
    """Player schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")
    age: Optional[int] = Field(None, description="Calculated age in years")


class PlayerResponse(PlayerInDB):
    """Player schema for API responses."""
    pass


class PlayerSummary(BaseModel):
    """Lightweight player summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    full_name: str = Field(..., description="Player's full name")
    known_as: Optional[str] = Field(None, description="Player's known name")
    batting_style: Optional[str] = Field(None, description="Batting style")
    bowling_style: Optional[str] = Field(None, description="Bowling style")

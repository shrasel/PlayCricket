"""Team schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas import TimestampMixin, PublicIdMixin


class TeamBase(BaseModel):
    """Base team schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Full team name")
    short_name: str = Field(..., min_length=1, max_length=10, description="Abbreviated team name")
    country_code: Optional[str] = Field(None, max_length=3, description="ISO country code")
    logo_url: Optional[HttpUrl] = Field(None, description="URL to team logo image")


class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    short_name: Optional[str] = Field(None, min_length=1, max_length=10)
    country_code: Optional[str] = Field(None, max_length=3)
    logo_url: Optional[HttpUrl] = None


class TeamInDB(TeamBase, PublicIdMixin, TimestampMixin):
    """Team schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class TeamResponse(TeamInDB):
    """Team schema for API responses."""
    pass


class TeamSummary(BaseModel):
    """Lightweight team summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    name: str = Field(..., description="Team name")
    short_name: str = Field(..., description="Abbreviated team name")
    logo_url: Optional[HttpUrl] = Field(None, description="Team logo URL")

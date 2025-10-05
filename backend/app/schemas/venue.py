"""Venue schemas for API requests and responses."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas import TimestampMixin, PublicIdMixin


class VenueBase(BaseModel):
    """Base venue schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Venue name")
    city: Optional[str] = Field(None, max_length=100, description="City where venue is located")
    country_code: Optional[str] = Field(None, max_length=3, description="ISO country code")
    timezone_name: Optional[str] = Field(None, max_length=64, description="IANA timezone name")
    ends_names: Optional[str] = Field(None, max_length=200, description="Names of the two ends (comma-separated)")


class VenueCreate(VenueBase):
    """Schema for creating a new venue."""
    pass


class VenueUpdate(BaseModel):
    """Schema for updating a venue (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=3)
    timezone_name: Optional[str] = Field(None, max_length=64)
    ends_names: Optional[str] = Field(None, max_length=200)


class VenueInDB(VenueBase, PublicIdMixin, TimestampMixin):
    """Venue schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class VenueResponse(VenueInDB):
    """Venue schema for API responses."""
    pass


class VenueSummary(BaseModel):
    """Lightweight venue summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    name: str = Field(..., description="Venue name")
    city: Optional[str] = Field(None, description="City")
    country_code: Optional[str] = Field(None, description="Country code")

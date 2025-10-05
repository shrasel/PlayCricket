"""Base schemas for common patterns."""
from datetime import datetime
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, ConfigDict, Field


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")


class PublicIdMixin(BaseModel):
    """Mixin for models with public ULID identifiers."""
    public_id: str = Field(..., min_length=26, max_length=26, description="Public ULID identifier")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    model_config = ConfigDict(from_attributes=True)
    
    total: int = Field(..., description="Total number of records")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    items: List[T] = Field(..., description="List of records")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    detail: Optional[str] = Field(None, description="Additional details")

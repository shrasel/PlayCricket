"""Delivery schemas for API requests and responses."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas import TimestampMixin, PublicIdMixin
from app.schemas.player import PlayerSummary


class DeliveryBase(BaseModel):
    """Base delivery schema with common fields."""
    innings_id: str = Field(..., description="Innings public ULID")
    over_number: int = Field(..., ge=1, description="Over number (1-based)")
    ball_in_over: int = Field(..., ge=1, le=6, description="Ball number in over (1-6, or more for extras)")
    is_legal_delivery: bool = Field(True, description="Legal delivery flag (false for wides/no-balls)")
    ts_utc: Optional[datetime] = Field(None, description="Timestamp when ball was bowled (UTC)")
    striker_id: str = Field(..., description="Striker public ULID")
    non_striker_id: str = Field(..., description="Non-striker public ULID")
    bowler_id: str = Field(..., description="Bowler public ULID")
    runs_batter: int = Field(0, ge=0, description="Runs scored by batter (0-6)")
    runs_extras: int = Field(0, ge=0, description="Extra runs (wides, no-balls, byes, leg-byes)")
    extra_type: Optional[str] = Field(None, max_length=20, description="WIDE, NO_BALL, BYE, LEG_BYE, PENALTY")
    is_four: bool = Field(False, description="Boundary flag (4 runs)")
    is_six: bool = Field(False, description="Six flag (6 runs)")
    wicket_type: Optional[str] = Field(
        None, 
        max_length=30, 
        description="BOWLED, CAUGHT, LBW, RUN_OUT, STUMPED, HIT_WICKET, CAUGHT_AND_BOWLED, OBSTRUCTING, HIT_BALL_TWICE, TIMED_OUT, RETIRED_HURT"
    )
    out_player_id: Optional[str] = Field(None, description="Dismissed player public ULID")
    fielder_id: Optional[str] = Field(None, description="Fielder public ULID (for catches/run-outs)")
    wagon_x: Optional[float] = Field(None, description="Shot wagon wheel X coordinate")
    wagon_y: Optional[float] = Field(None, description="Shot wagon wheel Y coordinate")
    pitch_x: Optional[float] = Field(None, description="Ball pitch map X coordinate")
    pitch_y: Optional[float] = Field(None, description="Ball pitch map Y coordinate")
    commentary_text: Optional[str] = Field(None, description="Ball-by-ball commentary")
    replaces_delivery_id: Optional[str] = Field(None, description="Delivery being corrected (for amendments)")


class DeliveryCreate(DeliveryBase):
    """Schema for creating a new delivery."""
    pass


class DeliveryUpdate(BaseModel):
    """Schema for updating a delivery (all fields optional)."""
    over_number: Optional[int] = Field(None, ge=1)
    ball_in_over: Optional[int] = Field(None, ge=1, le=6)
    is_legal_delivery: Optional[bool] = None
    ts_utc: Optional[datetime] = None
    striker_id: Optional[str] = None
    non_striker_id: Optional[str] = None
    bowler_id: Optional[str] = None
    runs_batter: Optional[int] = Field(None, ge=0)
    runs_extras: Optional[int] = Field(None, ge=0)
    extra_type: Optional[str] = Field(None, max_length=20)
    is_four: Optional[bool] = None
    is_six: Optional[bool] = None
    wicket_type: Optional[str] = Field(None, max_length=30)
    out_player_id: Optional[str] = None
    fielder_id: Optional[str] = None
    wagon_x: Optional[float] = None
    wagon_y: Optional[float] = None
    pitch_x: Optional[float] = None
    pitch_y: Optional[float] = None
    commentary_text: Optional[str] = None
    replaces_delivery_id: Optional[str] = None


class DeliveryInDB(DeliveryBase, PublicIdMixin, TimestampMixin):
    """Delivery schema as stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Internal database ID")


class DeliveryResponse(DeliveryInDB):
    """Delivery schema for API responses with nested relationships."""
    striker: Optional[PlayerSummary] = None
    non_striker: Optional[PlayerSummary] = None
    bowler: Optional[PlayerSummary] = None
    out_player: Optional[PlayerSummary] = None
    fielder: Optional[PlayerSummary] = None


class DeliverySummary(BaseModel):
    """Lightweight delivery summary for nested responses."""
    model_config = ConfigDict(from_attributes=True)
    
    public_id: str = Field(..., description="Public ULID identifier")
    over_number: int = Field(..., description="Over number")
    ball_in_over: int = Field(..., description="Ball number in over")
    runs_batter: int = Field(..., description="Runs scored by batter")
    runs_extras: int = Field(..., description="Extra runs")
    wicket_type: Optional[str] = Field(None, description="Wicket type if dismissal")
    striker: Optional[PlayerSummary] = None
    bowler: Optional[PlayerSummary] = None


class BallByBallRequest(BaseModel):
    """Comprehensive schema for recording a ball in live scoring."""
    # Required fields
    over_number: int = Field(..., ge=1, description="Current over number")
    ball_in_over: int = Field(..., ge=1, description="Ball number in current over")
    striker_id: str = Field(..., description="Striker player public ULID")
    non_striker_id: str = Field(..., description="Non-striker player public ULID")
    bowler_id: str = Field(..., description="Bowler player public ULID")
    
    # Runs and extras
    runs_batter: int = Field(0, ge=0, le=6, description="Runs scored by batter")
    runs_extras: int = Field(0, ge=0, description="Extra runs")
    extra_type: Optional[str] = Field(None, description="WIDE, NO_BALL, BYE, LEG_BYE, PENALTY")
    
    # Boundaries
    is_four: bool = Field(False, description="Boundary flag")
    is_six: bool = Field(False, description="Six flag")
    
    # Wickets
    wicket_type: Optional[str] = Field(None, description="Wicket type if dismissal occurred")
    out_player_id: Optional[str] = Field(None, description="Dismissed player public ULID")
    fielder_id: Optional[str] = Field(None, description="Fielder involved in dismissal")
    
    # Analytics
    wagon_x: Optional[float] = Field(None, description="Shot wagon wheel X")
    wagon_y: Optional[float] = Field(None, description="Shot wagon wheel Y")
    pitch_x: Optional[float] = Field(None, description="Pitch map X")
    pitch_y: Optional[float] = Field(None, description="Pitch map Y")
    
    # Commentary
    commentary_text: Optional[str] = Field(None, description="Ball commentary")

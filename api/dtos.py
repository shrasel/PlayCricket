"""
PlayCricket Platform - FastAPI DTOs and API Contracts
Angular-compatible data transfer objects for live scoring and statistics
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# =============================================================================
# ENUM CLASSES (for type safety)
# =============================================================================

class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    DELAYED = "DELAYED"
    LIVE = "LIVE"
    INNINGS_BREAK = "INNINGS_BREAK"
    RAIN_DELAY = "RAIN_DELAY"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    NO_RESULT = "NO_RESULT"

class ExtraType(str, Enum):
    NONE = "NONE"
    BYE = "BYE"
    LEGBYE = "LEGBYE"
    WIDE = "WIDE"
    NO_BALL = "NO_BALL"
    PENALTY = "PENALTY"

class WicketType(str, Enum):
    BOWLED = "BOWLED"
    LBW = "LBW"
    CAUGHT = "CAUGHT"
    CAUGHT_BEHIND = "CAUGHT_BEHIND"
    STUMPED = "STUMPED"
    RUN_OUT = "RUN_OUT"
    HIT_WICKET = "HIT_WICKET"

class CommentaryType(str, Enum):
    BALL = "BALL"
    OVER = "OVER"
    WICKET = "WICKET"
    BOUNDARY = "BOUNDARY"
    MILESTONE = "MILESTONE"
    GENERAL = "GENERAL"

# =============================================================================
# BASE MODELS
# =============================================================================

class BaseEntity(BaseModel):
    """Base model with common fields"""
    public_id: str = Field(..., description="Public ULID identifier")
    created_at: Optional[datetime] = None

class TeamBasic(BaseModel):
    """Basic team information"""
    public_id: str
    name: str
    short_name: str
    country_code: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None

class PlayerBasic(BaseModel):
    """Basic player information"""
    public_id: str
    full_name: str
    known_as: Optional[str] = None
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    nationality: Optional[str] = None

class VenueBasic(BaseModel):
    """Basic venue information"""
    public_id: str
    name: str
    city: Optional[str] = None
    country_code: Optional[str] = None
    timezone_name: str

# =============================================================================
# LIVE SCORING DTOs
# =============================================================================

class LiveDeliveryDTO(BaseModel):
    """Individual ball delivery for live updates"""
    public_id: str
    over_number: int = Field(..., description="0-based over number")
    ball_in_over: int = Field(..., description="1-6 ball number in over")
    is_legal_delivery: bool
    
    # Players
    striker: PlayerBasic
    non_striker: PlayerBasic
    bowler: PlayerBasic
    
    # Runs and extras
    runs_batter: int = 0
    runs_extras: int = 0
    extra_type: Optional[ExtraType] = None
    
    # Boundaries and wickets
    is_four: bool = False
    is_six: bool = False
    wicket_type: Optional[WicketType] = None
    out_player: Optional[PlayerBasic] = None
    fielder: Optional[PlayerBasic] = None
    
    # Commentary and timing
    commentary_text: Optional[str] = None
    timestamp: datetime
    
    # Analytics (optional)
    wagon_x: Optional[float] = None
    wagon_y: Optional[float] = None

class CurrentInningsDTO(BaseModel):
    """Current innings state for live center"""
    public_id: str
    seq_number: int
    batting_team: TeamBasic
    bowling_team: TeamBasic
    
    # Current totals
    total_runs: int = 0
    wickets_fallen: int = 0
    overs_completed: int = 0
    balls_in_current_over: int = 0
    current_run_rate: float = 0.0
    
    # Target chase info
    target_runs: Optional[int] = None
    required_runs: Optional[int] = None
    required_run_rate: Optional[float] = None
    required_balls: Optional[int] = None
    
    # Boundaries
    fours: int = 0
    sixes: int = 0
    
    # Current players
    striker: Optional[PlayerBasic] = None
    non_striker: Optional[PlayerBasic] = None
    bowler: Optional[PlayerBasic] = None
    
    # Match state
    is_powerplay: bool = False
    powerplay_type: Optional[str] = None
    
    # Recent deliveries (last 6 balls)
    recent_balls: List[str] = Field(default_factory=list, description="Last 6 balls as symbols: 1,2,3,4,6,W,•")

class LiveMatchCenterDTO(BaseModel):
    """Complete live match center data"""
    match_public_id: str
    status: MatchStatus
    
    # Teams and venue
    team1: TeamBasic
    team2: TeamBasic
    venue: VenueBasic
    
    # Current innings
    current_innings: Optional[CurrentInningsDTO] = None
    
    # Toss info
    toss_winner: Optional[TeamBasic] = None
    toss_decision: Optional[str] = None
    
    # Match result
    result_type: Optional[str] = None
    winner: Optional[TeamBasic] = None
    win_margin_runs: Optional[int] = None
    win_margin_wickets: Optional[int] = None
    
    # Live updates
    last_updated: datetime
    is_live_streaming: bool = False
    viewer_count: int = 0

# =============================================================================
# SCORECARD DTOs
# =============================================================================

class BattingCardRowDTO(BaseModel):
    """Individual batsman scorecard row"""
    player: PlayerBasic
    batting_order: Optional[int] = None
    is_captain: bool = False
    is_wicketkeeper: bool = False
    
    # Batting figures
    runs_scored: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    strike_rate: Optional[float] = None
    
    # Dismissal info
    dismissal_info: str = "not out"  # "not out", "did not bat", or dismissal description
    dismissed_by_bowler: Optional[str] = None
    dismissed_by_fielder: Optional[str] = None

class BowlingCardRowDTO(BaseModel):
    """Individual bowler figures row"""
    player: PlayerBasic
    
    # Bowling figures
    overs_bowled: str = "0.0"  # "15.4" format
    maidens: int = 0
    runs_conceded: int = 0
    wickets: int = 0
    economy_rate: float = 0.0
    
    # Additional stats
    fours_conceded: int = 0
    sixes_conceded: int = 0
    wides: int = 0
    no_balls: int = 0

class PartnershipDTO(BaseModel):
    """Partnership details"""
    partnership_number: int
    batsman1: PlayerBasic
    batsman2: PlayerBasic
    
    # Partnership stats
    partnership_runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    partnership_strike_rate: float = 0.0
    
    # Individual contributions
    batsman1_runs: int = 0
    batsman2_runs: int = 0

class InningsScorecardDTO(BaseModel):
    """Complete innings scorecard"""
    public_id: str
    seq_number: int
    batting_team: TeamBasic
    bowling_team: TeamBasic
    
    # Innings totals
    total_runs: int = 0
    wickets_fallen: int = 0
    overs_completed: int = 0
    current_run_rate: float = 0.0
    target_runs: Optional[int] = None
    
    # Extras breakdown
    byes: int = 0
    leg_byes: int = 0
    wides: int = 0
    no_balls: int = 0
    penalties: int = 0
    
    # Detailed cards
    batting_card: List[BattingCardRowDTO] = Field(default_factory=list)
    bowling_card: List[BowlingCardRowDTO] = Field(default_factory=list)
    partnerships: List[PartnershipDTO] = Field(default_factory=list)
    
    # Status
    is_completed: bool = False
    declared: bool = False

class MatchScorecardDTO(BaseModel):
    """Complete match scorecard"""
    match_public_id: str
    venue: VenueBasic
    start_time: datetime
    status: MatchStatus
    
    # Match result
    result_type: Optional[str] = None
    winner: Optional[TeamBasic] = None
    win_margin_runs: Optional[int] = None
    win_margin_wickets: Optional[int] = None
    win_method: Optional[str] = None
    
    # Toss
    toss_winner: Optional[TeamBasic] = None
    toss_decision: Optional[str] = None
    
    # Innings
    innings: List[InningsScorecardDTO] = Field(default_factory=list)

# =============================================================================
# CHARTS AND ANALYTICS DTOs  
# =============================================================================

class ManhattanDataPointDTO(BaseModel):
    """Single over data for Manhattan chart"""
    over_number: int
    runs_in_over: int = 0
    cumulative_runs: int = 0
    wickets_in_over: int = 0
    cumulative_wickets: int = 0
    over_run_rate: float = 0.0
    cumulative_run_rate: float = 0.0

class WagonWheelShotDTO(BaseModel):
    """Individual shot for wagon wheel"""
    player: PlayerBasic
    runs_scored: int
    shot_type: str  # "DOT", "SINGLE", "MULTIPLE", "FOUR", "SIX"
    is_four: bool = False
    is_six: bool = False
    
    # Coordinates (0-100 normalized)
    wagon_x: float
    wagon_y: float
    shot_zone: Optional[str] = None
    
    # Context
    over_number: int
    ball_in_over: int

class MatchAnalyticsDTO(BaseModel):
    """Match analytics for charts"""
    match_public_id: str
    
    # Manhattan chart data (over by over)
    manhattan_data: Dict[int, List[ManhattanDataPointDTO]] = Field(
        default_factory=dict, 
        description="Keyed by innings sequence number"
    )
    
    # Wagon wheel shots
    wagon_wheel_shots: Dict[str, List[WagonWheelShotDTO]] = Field(
        default_factory=dict,
        description="Keyed by player public_id"
    )
    
    # Worm chart (cumulative runs over overs)
    worm_data: Dict[int, List[Dict[str, Union[int, float]]]] = Field(
        default_factory=dict,
        description="Cumulative runs progression by innings"
    )

# =============================================================================
# TOURNAMENT AND LEAGUE DTOs
# =============================================================================

class LeagueTableRowDTO(BaseModel):
    """Single team row in league table"""
    position: int
    team: TeamBasic
    
    # Match statistics
    matches_played: int = 0
    matches_won: int = 0
    matches_lost: int = 0
    matches_tied: int = 0
    matches_no_result: int = 0
    points: int = 0
    
    # Performance metrics
    win_percentage: float = 0.0
    net_run_rate: float = 0.0
    qualification_status: str = "TBD"
    
    # Recent form (last 5 matches as W/L/T/N)
    recent_form: Optional[str] = None

class TournamentStandingsDTO(BaseModel):
    """Tournament standings/league table"""
    tournament_public_id: str
    tournament_name: str
    stage_name: Optional[str] = None
    
    # Table data
    standings: List[LeagueTableRowDTO] = Field(default_factory=list)
    
    # Points system
    points_system: Optional[Dict[str, int]] = None
    last_updated: datetime

class FixtureDTO(BaseModel):
    """Tournament fixture"""
    match_public_id: str
    stage_name: Optional[str] = None
    
    # Teams
    team1: TeamBasic
    team2: TeamBasic
    team1_position: Optional[int] = None
    team2_position: Optional[int] = None
    
    # Venue and timing
    venue: VenueBasic
    start_time: datetime
    local_start_time: Optional[str] = None
    
    # Match details
    match_type: str
    overs_limit: Optional[int] = None
    status: MatchStatus
    
    # Historical context
    head_to_head_record: Optional[str] = None

class TournamentOverviewDTO(BaseModel):
    """Tournament overview"""
    public_id: str
    name: str
    season_label: Optional[str] = None
    match_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Statistics
    total_matches: int = 0
    completed_matches: int = 0
    live_matches: int = 0
    upcoming_matches: int = 0
    total_teams: int = 0
    
    current_stage: Optional[str] = None

# =============================================================================
# LIVE COMMENTARY DTOs
# =============================================================================

class CommentaryItemDTO(BaseModel):
    """Individual commentary item"""
    id: int
    commentary_text: str
    commentary_type: CommentaryType
    timestamp: datetime
    is_key_moment: bool = False
    
    # Delivery context (if applicable)
    over_number: Optional[int] = None
    ball_in_over: Optional[int] = None
    runs_scored: Optional[int] = None
    
    # Player context
    striker: Optional[PlayerBasic] = None
    bowler: Optional[PlayerBasic] = None
    
    # Metadata
    commentator_name: Optional[str] = None

class LiveCommentaryFeedDTO(BaseModel):
    """Live commentary feed"""
    match_public_id: str
    commentary: List[CommentaryItemDTO] = Field(default_factory=list)
    total_items: int = 0
    last_updated: datetime

# =============================================================================
# REQUEST DTOs (for creating/updating data)
# =============================================================================

class CreateDeliveryRequestDTO(BaseModel):
    """Request to create a new delivery"""
    innings_public_id: str
    over_number: int
    ball_in_over: int
    is_legal_delivery: bool = True
    
    # Player public IDs
    striker_public_id: str
    non_striker_public_id: str
    bowler_public_id: str
    wicketkeeper_public_id: Optional[str] = None
    
    # Runs and extras
    runs_batter: int = 0
    runs_extras: int = 0
    extra_type: Optional[ExtraType] = None
    
    # Boundaries and wickets
    is_four: bool = False
    is_six: bool = False
    wicket_type: Optional[WicketType] = None
    out_player_public_id: Optional[str] = None
    fielder_public_id: Optional[str] = None
    
    # Commentary and analytics
    commentary_text: Optional[str] = None
    wagon_x: Optional[float] = None
    wagon_y: Optional[float] = None
    shot_zone: Optional[str] = None
    
    # Timing
    timestamp: Optional[datetime] = None

class UpdateMatchStatusRequestDTO(BaseModel):
    """Request to update match status"""
    match_public_id: str
    status: MatchStatus
    current_striker_public_id: Optional[str] = None
    current_non_striker_public_id: Optional[str] = None
    current_bowler_public_id: Optional[str] = None

class CreateCommentaryRequestDTO(BaseModel):
    """Request to create commentary"""
    match_public_id: str
    commentary_text: str
    commentary_type: CommentaryType = CommentaryType.GENERAL
    delivery_public_id: Optional[str] = None
    is_key_moment: bool = False
    commentator_name: Optional[str] = None

# =============================================================================
# RESPONSE DTOs
# =============================================================================

class ApiResponseDTO(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponseDTO(BaseModel):
    """Paginated response wrapper"""
    items: List[Any] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_previous: bool = False

# =============================================================================
# WEBSOCKET EVENT DTOs
# =============================================================================

class WebSocketEventDTO(BaseModel):
    """WebSocket event for real-time updates"""
    event_type: str  # "DELIVERY", "WICKET", "BOUNDARY", "OVER_COMPLETE", "INNINGS_BREAK"
    match_public_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)

class LiveScoreUpdateDTO(BaseModel):
    """Live score update event"""
    match_public_id: str
    current_innings: CurrentInningsDTO
    latest_delivery: Optional[LiveDeliveryDTO] = None
    latest_commentary: Optional[CommentaryItemDTO] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
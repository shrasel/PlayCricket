// PlayCricket Platform - Angular Service Interfaces
// TypeScript interfaces matching FastAPI DTOs for type-safe frontend development

// =============================================================================
// ENUM TYPES
// =============================================================================

export enum MatchStatus {
  SCHEDULED = 'SCHEDULED',
  DELAYED = 'DELAYED',
  LIVE = 'LIVE',
  INNINGS_BREAK = 'INNINGS_BREAK',
  RAIN_DELAY = 'RAIN_DELAY',
  COMPLETED = 'COMPLETED',
  ABANDONED = 'ABANDONED',
  NO_RESULT = 'NO_RESULT'
}

export enum ExtraType {
  NONE = 'NONE',
  BYE = 'BYE',
  LEGBYE = 'LEGBYE',
  WIDE = 'WIDE',
  NO_BALL = 'NO_BALL',
  PENALTY = 'PENALTY'
}

export enum WicketType {
  BOWLED = 'BOWLED',
  LBW = 'LBW',
  CAUGHT = 'CAUGHT',
  CAUGHT_BEHIND = 'CAUGHT_BEHIND',
  STUMPED = 'STUMPED',
  RUN_OUT = 'RUN_OUT',
  HIT_WICKET = 'HIT_WICKET'
}

export enum CommentaryType {
  BALL = 'BALL',
  OVER = 'OVER',
  WICKET = 'WICKET',
  BOUNDARY = 'BOUNDARY',
  MILESTONE = 'MILESTONE',
  GENERAL = 'GENERAL'
}

// =============================================================================
// BASE INTERFACES
// =============================================================================

export interface BaseEntity {
  public_id: string;
  created_at?: string;
}

export interface TeamBasic {
  public_id: string;
  name: string;
  short_name: string;
  country_code?: string;
  primary_color?: string;
  secondary_color?: string;
}

export interface PlayerBasic {
  public_id: string;
  full_name: string;
  known_as?: string;
  batting_style?: string;
  bowling_style?: string;
  nationality?: string;
}

export interface VenueBasic {
  public_id: string;
  name: string;
  city?: string;
  country_code?: string;
  timezone_name: string;
}

// =============================================================================
// LIVE SCORING INTERFACES
// =============================================================================

export interface LiveDelivery {
  public_id: string;
  over_number: number;
  ball_in_over: number;
  is_legal_delivery: boolean;
  
  // Players
  striker: PlayerBasic;
  non_striker: PlayerBasic;
  bowler: PlayerBasic;
  
  // Runs and extras
  runs_batter: number;
  runs_extras: number;
  extra_type?: ExtraType;
  
  // Boundaries and wickets
  is_four: boolean;
  is_six: boolean;
  wicket_type?: WicketType;
  out_player?: PlayerBasic;
  fielder?: PlayerBasic;
  
  // Commentary and timing
  commentary_text?: string;
  timestamp: string;
  
  // Analytics (optional)
  wagon_x?: number;
  wagon_y?: number;
}

export interface CurrentInnings {
  public_id: string;
  seq_number: number;
  batting_team: TeamBasic;
  bowling_team: TeamBasic;
  
  // Current totals
  total_runs: number;
  wickets_fallen: number;
  overs_completed: number;
  balls_in_current_over: number;
  current_run_rate: number;
  
  // Target chase info
  target_runs?: number;
  required_runs?: number;
  required_run_rate?: number;
  required_balls?: number;
  
  // Boundaries
  fours: number;
  sixes: number;
  
  // Current players
  striker?: PlayerBasic;
  non_striker?: PlayerBasic;
  bowler?: PlayerBasic;
  
  // Match state
  is_powerplay: boolean;
  powerplay_type?: string;
  
  // Recent deliveries (last 6 balls)
  recent_balls: string[];
}

export interface LiveMatchCenter {
  match_public_id: string;
  status: MatchStatus;
  
  // Teams and venue
  team1: TeamBasic;
  team2: TeamBasic;
  venue: VenueBasic;
  
  // Current innings
  current_innings?: CurrentInnings;
  
  // Toss info
  toss_winner?: TeamBasic;
  toss_decision?: string;
  
  // Match result
  result_type?: string;
  winner?: TeamBasic;
  win_margin_runs?: number;
  win_margin_wickets?: number;
  
  // Live updates
  last_updated: string;
  is_live_streaming: boolean;
  viewer_count: number;
}

// =============================================================================
// SCORECARD INTERFACES
// =============================================================================

export interface BattingCardRow {
  player: PlayerBasic;
  batting_order?: number;
  is_captain: boolean;
  is_wicketkeeper: boolean;
  
  // Batting figures
  runs_scored: number;
  balls_faced: number;
  fours: number;
  sixes: number;
  strike_rate?: number;
  
  // Dismissal info
  dismissal_info: string;
  dismissed_by_bowler?: string;
  dismissed_by_fielder?: string;
}

export interface BowlingCardRow {
  player: PlayerBasic;
  
  // Bowling figures
  overs_bowled: string;
  maidens: number;
  runs_conceded: number;
  wickets: number;
  economy_rate: number;
  
  // Additional stats
  fours_conceded: number;
  sixes_conceded: number;
  wides: number;
  no_balls: number;
}

export interface Partnership {
  partnership_number: number;
  batsman1: PlayerBasic;
  batsman2: PlayerBasic;
  
  // Partnership stats
  partnership_runs: number;
  balls_faced: number;
  fours: number;
  sixes: number;
  partnership_strike_rate: number;
  
  // Individual contributions
  batsman1_runs: number;
  batsman2_runs: number;
}

export interface InningsScorecard {
  public_id: string;
  seq_number: number;
  batting_team: TeamBasic;
  bowling_team: TeamBasic;
  
  // Innings totals
  total_runs: number;
  wickets_fallen: number;
  overs_completed: number;
  current_run_rate: number;
  target_runs?: number;
  
  // Extras breakdown
  byes: number;
  leg_byes: number;
  wides: number;
  no_balls: number;
  penalties: number;
  
  // Detailed cards
  batting_card: BattingCardRow[];
  bowling_card: BowlingCardRow[];
  partnerships: Partnership[];
  
  // Status
  is_completed: boolean;
  declared: boolean;
}

export interface MatchScorecard {
  match_public_id: string;
  venue: VenueBasic;
  start_time: string;
  status: MatchStatus;
  
  // Match result
  result_type?: string;
  winner?: TeamBasic;
  win_margin_runs?: number;
  win_margin_wickets?: number;
  win_method?: string;
  
  // Toss
  toss_winner?: TeamBasic;
  toss_decision?: string;
  
  // Innings
  innings: InningsScorecard[];
}

// =============================================================================
// CHARTS AND ANALYTICS INTERFACES
// =============================================================================

export interface ManhattanDataPoint {
  over_number: number;
  runs_in_over: number;
  cumulative_runs: number;
  wickets_in_over: number;
  cumulative_wickets: number;
  over_run_rate: number;
  cumulative_run_rate: number;
}

export interface WagonWheelShot {
  player: PlayerBasic;
  runs_scored: number;
  shot_type: 'DOT' | 'SINGLE' | 'MULTIPLE' | 'FOUR' | 'SIX';
  is_four: boolean;
  is_six: boolean;
  
  // Coordinates (0-100 normalized)
  wagon_x: number;
  wagon_y: number;
  shot_zone?: string;
  
  // Context
  over_number: number;
  ball_in_over: number;
}

export interface MatchAnalytics {
  match_public_id: string;
  
  // Manhattan chart data (keyed by innings sequence number)
  manhattan_data: { [inningsNumber: number]: ManhattanDataPoint[] };
  
  // Wagon wheel shots (keyed by player public_id)
  wagon_wheel_shots: { [playerPublicId: string]: WagonWheelShot[] };
  
  // Worm chart (cumulative runs over overs)
  worm_data: { [inningsNumber: number]: Array<{ over: number; runs: number }> };
}

// =============================================================================
// TOURNAMENT AND LEAGUE INTERFACES
// =============================================================================

export interface LeagueTableRow {
  position: number;
  team: TeamBasic;
  
  // Match statistics
  matches_played: number;
  matches_won: number;
  matches_lost: number;
  matches_tied: number;
  matches_no_result: number;
  points: number;
  
  // Performance metrics
  win_percentage: number;
  net_run_rate: number;
  qualification_status: string;
  
  // Recent form (last 5 matches as W/L/T/N)
  recent_form?: string;
}

export interface TournamentStandings {
  tournament_public_id: string;
  tournament_name: string;
  stage_name?: string;
  
  // Table data
  standings: LeagueTableRow[];
  
  // Points system
  points_system?: { [result: string]: number };
  last_updated: string;
}

export interface Fixture {
  match_public_id: string;
  stage_name?: string;
  
  // Teams
  team1: TeamBasic;
  team2: TeamBasic;
  team1_position?: number;
  team2_position?: number;
  
  // Venue and timing
  venue: VenueBasic;
  start_time: string;
  local_start_time?: string;
  
  // Match details
  match_type: string;
  overs_limit?: number;
  status: MatchStatus;
  
  // Historical context
  head_to_head_record?: string;
}

export interface TournamentOverview {
  public_id: string;
  name: string;
  season_label?: string;
  match_type: string;
  start_date?: string;
  end_date?: string;
  
  // Statistics
  total_matches: number;
  completed_matches: number;
  live_matches: number;
  upcoming_matches: number;
  total_teams: number;
  
  current_stage?: string;
}

// =============================================================================
// LIVE COMMENTARY INTERFACES
// =============================================================================

export interface CommentaryItem {
  id: number;
  commentary_text: string;
  commentary_type: CommentaryType;
  timestamp: string;
  is_key_moment: boolean;
  
  // Delivery context (if applicable)
  over_number?: number;
  ball_in_over?: number;
  runs_scored?: number;
  
  // Player context
  striker?: PlayerBasic;
  bowler?: PlayerBasic;
  
  // Metadata
  commentator_name?: string;
}

export interface LiveCommentaryFeed {
  match_public_id: string;
  commentary: CommentaryItem[];
  total_items: number;
  last_updated: string;
}

// =============================================================================
// REQUEST INTERFACES
// =============================================================================

export interface CreateDeliveryRequest {
  innings_public_id: string;
  over_number: number;
  ball_in_over: number;
  is_legal_delivery: boolean;
  
  // Player public IDs
  striker_public_id: string;
  non_striker_public_id: string;
  bowler_public_id: string;
  wicketkeeper_public_id?: string;
  
  // Runs and extras
  runs_batter: number;
  runs_extras: number;
  extra_type?: ExtraType;
  
  // Boundaries and wickets
  is_four: boolean;
  is_six: boolean;
  wicket_type?: WicketType;
  out_player_public_id?: string;
  fielder_public_id?: string;
  
  // Commentary and analytics
  commentary_text?: string;
  wagon_x?: number;
  wagon_y?: number;
  shot_zone?: string;
  
  // Timing
  timestamp?: string;
}

export interface UpdateMatchStatusRequest {
  match_public_id: string;
  status: MatchStatus;
  current_striker_public_id?: string;
  current_non_striker_public_id?: string;
  current_bowler_public_id?: string;
}

export interface CreateCommentaryRequest {
  match_public_id: string;
  commentary_text: string;
  commentary_type: CommentaryType;
  delivery_public_id?: string;
  is_key_moment: boolean;
  commentator_name?: string;
}

// =============================================================================
// RESPONSE INTERFACES
// =============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  errors?: string[];
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// =============================================================================
// WEBSOCKET EVENT INTERFACES
// =============================================================================

export interface WebSocketEvent {
  event_type: 'DELIVERY' | 'WICKET' | 'BOUNDARY' | 'OVER_COMPLETE' | 'INNINGS_BREAK';
  match_public_id: string;
  timestamp: string;
  data: { [key: string]: any };
}

export interface LiveScoreUpdate {
  match_public_id: string;
  current_innings: CurrentInnings;
  latest_delivery?: LiveDelivery;
  latest_commentary?: CommentaryItem;
  updated_at: string;
}

// =============================================================================
// ANGULAR SERVICE METHOD SIGNATURES
// =============================================================================

export interface CricketApiService {
  // Live scoring
  getLiveMatchCenter(matchPublicId: string): Promise<ApiResponse<LiveMatchCenter>>;
  getMatchScorecard(matchPublicId: string): Promise<ApiResponse<MatchScorecard>>;
  createDelivery(request: CreateDeliveryRequest): Promise<ApiResponse<LiveDelivery>>;
  updateMatchStatus(request: UpdateMatchStatusRequest): Promise<ApiResponse<void>>;
  
  // Analytics and charts
  getMatchAnalytics(matchPublicId: string): Promise<ApiResponse<MatchAnalytics>>;
  getManhattanData(matchPublicId: string, inningsNumber?: number): Promise<ApiResponse<ManhattanDataPoint[]>>;
  getWagonWheelData(matchPublicId: string, playerPublicId?: string): Promise<ApiResponse<WagonWheelShot[]>>;
  
  // Tournament and league
  getTournamentStandings(tournamentPublicId: string, stageId?: string): Promise<ApiResponse<TournamentStandings>>;
  getTournamentFixtures(tournamentPublicId: string, upcoming?: boolean): Promise<ApiResponse<Fixture[]>>;
  getTournamentOverview(tournamentPublicId: string): Promise<ApiResponse<TournamentOverview>>;
  
  // Commentary
  getLiveCommentary(matchPublicId: string, limit?: number): Promise<ApiResponse<LiveCommentaryFeed>>;
  createCommentary(request: CreateCommentaryRequest): Promise<ApiResponse<CommentaryItem>>;
  
  // Search and lists
  searchMatches(query?: string, status?: MatchStatus[], limit?: number): Promise<ApiResponse<PaginatedResponse<LiveMatchCenter>>>;
  getRecentMatches(limit?: number): Promise<ApiResponse<LiveMatchCenter[]>>;
  getLiveMatches(): Promise<ApiResponse<LiveMatchCenter[]>>;
}

// =============================================================================
// WEBSOCKET SERVICE INTERFACE
// =============================================================================

export interface CricketWebSocketService {
  // Connection management
  connect(): void;
  disconnect(): void;
  isConnected(): boolean;
  
  // Match subscriptions
  subscribeToMatch(matchPublicId: string): void;
  unsubscribeFromMatch(matchPublicId: string): void;
  
  // Event observables
  onLiveScoreUpdate(): any; // Observable<LiveScoreUpdate>
  onCommentaryUpdate(): any; // Observable<CommentaryItem>
  onMatchStatusChange(): any; // Observable<MatchStatus>
  onConnectionStatus(): any; // Observable<boolean>
  
  // Event emitters
  sendDelivery(delivery: CreateDeliveryRequest): void;
  sendCommentary(commentary: CreateCommentaryRequest): void;
}

// =============================================================================
// CHART COMPONENT DATA INTERFACES
// =============================================================================

export interface ManhattanChartConfig {
  data: ManhattanDataPoint[];
  showRunRate: boolean;
  showWickets: boolean;
  height: number;
  colors: {
    runs: string;
    runRate: string;
    wickets: string;
  };
}

export interface WagonWheelChartConfig {
  shots: WagonWheelShot[];
  fieldDimensions: {
    width: number;
    height: number;
  };
  showOnlyBoundaries: boolean;
  colors: {
    dot: string;
    single: string;
    boundary: string;
    six: string;
  };
}

export interface WormChartConfig {
  data: Array<{
    over: number;
    team1_runs?: number;
    team2_runs?: number;
    team1_wickets?: number;
    team2_wickets?: number;
  }>;
  showProjection: boolean;
  targetRuns?: number;
  colors: {
    team1: string;
    team2: string;
    target: string;
  };
}
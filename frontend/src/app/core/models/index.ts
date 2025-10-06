// Base interfaces
export interface TimestampMixin {
  created_at: string;
  updated_at: string;
}

export interface PublicIdMixin {
  public_id: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Team interfaces
export interface Team extends TimestampMixin, PublicIdMixin {
  id: number;
  name: string;
  short_name: string;
  country_code?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
}

export interface TeamCreate {
  name: string;
  short_name: string;
  country_code?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
}

export interface TeamUpdate {
  name?: string;
  short_name?: string;
  country_code?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
}

export interface TeamSummary {
  public_id: string;
  name: string;
  short_name: string;
  logo_url?: string;
}

// Player interfaces
export enum BattingStyle {
  RIGHT_HAND = 'RIGHT_HAND',
  LEFT_HAND = 'LEFT_HAND'
}

export enum BowlingStyle {
  RIGHT_ARM_FAST = 'RIGHT_ARM_FAST',
  LEFT_ARM_FAST = 'LEFT_ARM_FAST',
  RIGHT_ARM_MEDIUM = 'RIGHT_ARM_MEDIUM',
  LEFT_ARM_MEDIUM = 'LEFT_ARM_MEDIUM',
  RIGHT_ARM_OFF_SPIN = 'RIGHT_ARM_OFF_SPIN',
  LEFT_ARM_ORTHODOX = 'LEFT_ARM_ORTHODOX',
  RIGHT_ARM_LEG_SPIN = 'RIGHT_ARM_LEG_SPIN',
  LEFT_ARM_CHINAMAN = 'LEFT_ARM_CHINAMAN',
  NONE = 'NONE'
}

export enum PlayerRole {
  BATSMAN = 'BATSMAN',
  BOWLER = 'BOWLER',
  ALL_ROUNDER = 'ALL_ROUNDER',
  WICKET_KEEPER = 'WICKET_KEEPER'
}

export interface Player extends TimestampMixin, PublicIdMixin {
  id: number;
  full_name: string;
  known_as?: string;
  dob?: string;
  batting_style?: string;
  bowling_style?: string;
  age?: number;
}

export interface PlayerCreate {
  full_name: string;
  known_as?: string;
  dob?: string;
  batting_style?: string;
  bowling_style?: string;
}

export interface PlayerUpdate {
  full_name?: string;
  known_as?: string;
  dob?: string;
  batting_style?: string;
  bowling_style?: string;
}

export interface PlayerSummary {
  public_id: string;
  full_name: string;
  known_as?: string;
  batting_style?: string;
  bowling_style?: string;
}

// Venue interfaces
export interface Venue extends TimestampMixin, PublicIdMixin {
  id: number;
  name: string;
  city?: string;
  country_code?: string;
  timezone_name?: string;
  ends_names?: string;
}

export interface VenueCreate {
  name: string;
  city?: string;
  country_code?: string;
  timezone_name?: string;
  ends_names?: string;
}

export interface VenueUpdate {
  name?: string;
  city?: string;
  country_code?: string;
  timezone_name?: string;
  ends_names?: string;
}

export interface VenueSummary {
  public_id: string;
  name: string;
  city?: string;
  country_code?: string;
}

// Tournament interfaces
export enum MatchType {
  TEST = 'TEST',
  ODI = 'ODI',
  T20 = 'T20',
  T10 = 'T10',
  THE_HUNDRED = 'THE_HUNDRED'
}

export interface Tournament extends TimestampMixin, PublicIdMixin {
  id: number;
  name: string;
  short_name?: string;
  season?: string;
  match_type?: string;
  start_date?: string;
  end_date?: string;
  points_system?: Record<string, any>;
}

export interface TournamentCreate {
  name: string;
  short_name?: string;
  season?: string;
  match_type?: string;
  start_date?: string;
  end_date?: string;
  points_system?: Record<string, any>;
}

export interface TournamentUpdate {
  name?: string;
  short_name?: string;
  season?: string;
  match_type?: string;
  start_date?: string;
  end_date?: string;
  points_system?: Record<string, any>;
}

export interface TournamentSummary {
  public_id: string;
  name: string;
  short_name?: string;
  season?: string;
  match_type?: string;
}

// Match interfaces
export enum MatchStatus {
  SCHEDULED = 'SCHEDULED',
  LIVE = 'LIVE',
  COMPLETED = 'COMPLETED',
  ABANDONED = 'ABANDONED',
  CANCELLED = 'CANCELLED'
}

export enum TossDecision {
  BAT = 'BAT',
  BOWL = 'BOWL'
}

export interface MatchTeam {
  team_id: string;
  is_home: boolean;
}

export interface MatchToss {
  toss_winner_id: string;
  elected_to: 'BAT' | 'BOWL';
}

export interface Match extends TimestampMixin, PublicIdMixin {
  id: number;
  venue_id: string;
  tournament_id?: string;
  match_number?: string;
  match_type: MatchType;
  status: MatchStatus;
  scheduled_start?: string;
  actual_start?: string;
  end_time?: string;
  overs_per_innings?: number;
  is_day_night: boolean;
  is_neutral_venue: boolean;
  result_type?: string;
  winning_team_id?: string;
  result_margin?: string;
  venue?: VenueSummary;
  tournament?: TournamentSummary;
  teams?: TeamSummary[];
  toss_winner?: TeamSummary;
  winning_team?: TeamSummary;
}

export interface MatchCreate {
  venue_id: string;
  tournament_id?: string;
  match_number?: string;
  match_type: MatchType;
  status?: MatchStatus;
  scheduled_start?: string;
  actual_start?: string;
  end_time?: string;
  overs_per_innings?: number;
  is_day_night?: boolean;
  is_neutral_venue?: boolean;
  result_type?: string;
  winning_team_id?: string;
  result_margin?: string;
  teams: MatchTeam[];
  toss?: MatchToss;
}

export interface MatchUpdate {
  venue_id?: string;
  tournament_id?: string;
  match_number?: string;
  match_type?: MatchType;
  status?: MatchStatus;
  scheduled_start?: string;
  actual_start?: string;
  end_time?: string;
  overs_per_innings?: number;
  is_day_night?: boolean;
  is_neutral_venue?: boolean;
  result_type?: string;
  winning_team_id?: string;
  result_margin?: string;
}

export interface TossInfo {
  toss_winner_id: string;
  elected_to: 'BAT' | 'BOWL';
}

// Innings interfaces
export enum InningsType {
  FIRST = 'FIRST',
  SECOND = 'SECOND',
  THIRD = 'THIRD',
  FOURTH = 'FOURTH',
  SUPER_OVER = 'SUPER_OVER'
}

export interface Innings extends TimestampMixin, PublicIdMixin {
  id: number;
  match_id: number;
  innings_number: number;
  innings_type: InningsType;
  batting_team_id: number;
  bowling_team_id: number;
  total_runs?: number;
  total_wickets?: number;
  total_overs?: number;
  is_declared: boolean;
  is_forfeited: boolean;
  is_all_out: boolean;
  target?: number;
}

export interface InningsCreate {
  match_id: number;
  innings_number: number;
  innings_type: InningsType;
  batting_team_id: number;
  bowling_team_id: number;
  target?: number;
}

export interface InningsUpdate extends Partial<InningsCreate> {}

export interface InningsScore {
  total_runs: number;
  total_wickets: number;
  total_overs: number;
  is_all_out: boolean;
  run_rate: number;
}

export interface Partnership {
  runs: number;
  balls: number;
  batsman1_id: number;
  batsman2_id: number;
  batsman1_runs: number;
  batsman2_runs: number;
}

// Delivery interfaces
export enum DismissalType {
  BOWLED = 'BOWLED',
  CAUGHT = 'CAUGHT',
  LBW = 'LBW',
  RUN_OUT = 'RUN_OUT',
  STUMPED = 'STUMPED',
  HIT_WICKET = 'HIT_WICKET',
  RETIRED_HURT = 'RETIRED_HURT',
  TIMED_OUT = 'TIMED_OUT',
  OBSTRUCTING_FIELD = 'OBSTRUCTING_FIELD'
}

export interface Delivery extends TimestampMixin, PublicIdMixin {
  id: number;
  innings_id: number;
  over_number: number;
  ball_number: number;
  bowler_id: number;
  batsman_id: number;
  non_striker_id: number;
  runs_scored: number;
  extras_type?: string;
  extras_runs: number;
  is_wicket: boolean;
  dismissal_type?: DismissalType;
  fielder_id?: number;
  is_boundary: boolean;
  is_six: boolean;
  is_dot_ball: boolean;
  is_legal_delivery: boolean;
  shot_x?: number;
  shot_y?: number;
  pitch_x?: number;
  pitch_y?: number;
  commentary?: string;
}

export interface DeliveryCreate {
  innings_id: number;
  over_number: number;
  ball_number: number;
  bowler_id: number;
  batsman_id: number;
  non_striker_id: number;
  runs_scored: number;
  extras_type?: string;
  extras_runs?: number;
  is_wicket?: boolean;
  dismissal_type?: DismissalType;
  fielder_id?: number;
  shot_x?: number;
  shot_y?: number;
  pitch_x?: number;
  pitch_y?: number;
  commentary?: string;
}

export interface BallByBallRequest extends DeliveryCreate {}

export interface BatsmanStats {
  runs: number;
  balls: number;
  fours: number;
  sixes: number;
  strike_rate: number;
}

export interface BowlerStats {
  overs: number;
  maidens: number;
  runs: number;
  wickets: number;
  economy: number;
  wide_balls: number;
  no_balls: number;
}

// Statistics interfaces
export interface Scorecard {
  match_id: number;
  innings_number: number;
  batting_team: TeamSummary;
  bowling_team: TeamSummary;
  total_runs: number;
  total_wickets: number;
  total_overs: number;
  batting_table: BattingPerformance[];
  bowling_table: BowlingPerformance[];
}

export interface BattingPerformance {
  player: PlayerSummary;
  runs: number;
  balls: number;
  fours: number;
  sixes: number;
  strike_rate: number;
  dismissal?: string;
}

export interface BowlingPerformance {
  player: PlayerSummary;
  overs: number;
  maidens: number;
  runs: number;
  wickets: number;
  economy: number;
  extras: number;
}

export interface CareerStats {
  player: PlayerSummary;
  batting: {
    matches: number;
    innings: number;
    runs: number;
    highest_score: number;
    average: number;
    strike_rate: number;
    hundreds: number;
    fifties: number;
  };
  bowling: {
    matches: number;
    innings: number;
    wickets: number;
    best_figures: string;
    average: number;
    economy: number;
    five_wickets: number;
  };
}

export interface MatchSummary {
  match: Match;
  teams: TeamSummary[];
  venue: VenueSummary;
  tournament?: TournamentSummary;
  innings_summaries: InningsScore[];
}

// Visualization interfaces
export interface WagonWheelData {
  shots: Array<{
    x: number;
    y: number;
    runs: number;
    is_boundary: boolean;
    is_six: boolean;
  }>;
}

export interface PitchMapData {
  balls: Array<{
    x: number;
    y: number;
    runs: number;
    is_wicket: boolean;
  }>;
}

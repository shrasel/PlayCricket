-- PlayCricket Platform - Core Schema Migration 001
-- SQLite-first with Postgres/MySQL compatibility notes
-- 
-- POSTGRES DIFFERENCES:
-- - Change BIGINT to BIGINT GENERATED ALWAYS AS IDENTITY  
-- - Use TIMESTAMPTZ instead of VARCHAR(32) for timestamps
-- - JSON fields use JSONB type instead of TEXT
-- 
-- MYSQL DIFFERENCES:
-- - Use BIGINT AUTO_INCREMENT PRIMARY KEY
-- - JSON fields use JSON type
-- - Use CHAR(26) for ULID storage with charset utf8mb4_bin

-- ENUM TABLES (replace CHECK constraints for MySQL compatibility)
CREATE TABLE enum_match_type (
  id INTEGER PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_extra_type (
  id INTEGER PRIMARY KEY, 
  code VARCHAR(16) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_wicket_type (
  id INTEGER PRIMARY KEY,
  code VARCHAR(24) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_stage_type (
  id INTEGER PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_match_status (
  id INTEGER PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_toss_decision (
  id INTEGER PRIMARY KEY,
  code VARCHAR(8) UNIQUE NOT NULL,
  description VARCHAR(32) NOT NULL
);

CREATE TABLE enum_player_role (
  id INTEGER PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

CREATE TABLE enum_batting_style (
  id INTEGER PRIMARY KEY,
  code VARCHAR(8) UNIQUE NOT NULL,
  description VARCHAR(32) NOT NULL
);

CREATE TABLE enum_bowling_style (
  id INTEGER PRIMARY KEY,
  code VARCHAR(32) UNIQUE NOT NULL,
  description VARCHAR(64) NOT NULL
);

-- CORE ENTITIES
CREATE TABLE team (
  id INTEGER PRIMARY KEY, -- SQLite: auto-increment; Postgres: GENERATED ALWAYS AS IDENTITY
  public_id TEXT UNIQUE NOT NULL, -- ULID as TEXT for SQLite; Postgres: can use UUID type
  name TEXT NOT NULL,
  short_name TEXT NOT NULL,
  country_code TEXT(3),
  logo_url TEXT,
  primary_color TEXT(7), -- Hex color codes
  secondary_color TEXT(7),
  created_at_utc TEXT NOT NULL, -- ISO8601; Postgres: TIMESTAMPTZ
  UNIQUE(name),
  UNIQUE(short_name)
);

CREATE TABLE player (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  known_as TEXT,
  date_of_birth DATE,
  batting_style_id INTEGER REFERENCES enum_batting_style(id),
  bowling_style_id INTEGER REFERENCES enum_bowling_style(id),
  birth_place TEXT,
  nationality TEXT(3),
  height_cm INTEGER,
  created_at_utc TEXT NOT NULL
);

-- Player career with teams (handles transfers/contracts)
CREATE TABLE team_player (
  id INTEGER PRIMARY KEY,
  team_id INTEGER NOT NULL REFERENCES team(id) ON DELETE RESTRICT,
  player_id INTEGER NOT NULL REFERENCES player(id) ON DELETE RESTRICT,
  role_id INTEGER REFERENCES enum_player_role(id),
  shirt_number INTEGER,
  start_date DATE NOT NULL,
  end_date DATE, -- NULL = active
  is_overseas BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE(team_id, player_id, start_date),
  UNIQUE(team_id, shirt_number, start_date) -- No duplicate shirt numbers in same period
);

CREATE TABLE venue (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  city TEXT,
  country_code TEXT(3),
  timezone_name TEXT NOT NULL, -- IANA timezone
  capacity INTEGER,
  ends_names TEXT, -- JSON array: ["Pavilion End", "City End"] 
  pitch_type TEXT, -- "Batting", "Bowling", "Balanced"
  elevation_m INTEGER,
  coordinates_lat REAL,
  coordinates_lng REAL,
  created_at_utc TEXT NOT NULL,
  UNIQUE(name, city)
);

-- Officials (umpires, match referees, scorers)
CREATE TABLE official (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  country_code TEXT(3),
  role TEXT NOT NULL, -- "UMPIRE", "REFEREE", "SCORER", "TV_UMPIRE"
  created_at_utc TEXT NOT NULL
);

CREATE TABLE tournament (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  season_label TEXT,
  match_type_id INTEGER NOT NULL REFERENCES enum_match_type(id),
  start_date DATE,
  end_date DATE,
  points_system TEXT, -- JSON: {"win":2,"tie":1,"loss":0,"no_result":1}
  created_at_utc TEXT NOT NULL,
  UNIQUE(name, season_label)
);

CREATE TABLE tournament_stage (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  tournament_id INTEGER NOT NULL REFERENCES tournament(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  stage_type_id INTEGER NOT NULL REFERENCES enum_stage_type(id),
  sort_order INTEGER NOT NULL,
  start_date DATE,
  end_date DATE
);

CREATE TABLE tournament_team (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournament(id) ON DELETE CASCADE,
  team_id INTEGER NOT NULL REFERENCES team(id) ON DELETE RESTRICT,
  group_name TEXT, -- "Group A", "Pool 1", etc.
  seed_number INTEGER,
  UNIQUE(tournament_id, team_id)
);

CREATE TABLE match (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  tournament_id INTEGER REFERENCES tournament(id),
  stage_id INTEGER REFERENCES tournament_stage(id),
  venue_id INTEGER NOT NULL REFERENCES venue(id),
  match_type_id INTEGER NOT NULL REFERENCES enum_match_type(id),
  status_id INTEGER NOT NULL REFERENCES enum_match_status(id),
  
  -- Scheduling
  start_time_utc TEXT, -- ISO8601
  local_start_time TEXT, -- "2024-10-05 14:30:00"
  timezone_name TEXT,
  
  -- Format specifics  
  overs_limit INTEGER, -- NULL for unlimited (Tests)
  balls_per_over INTEGER NOT NULL DEFAULT 6,
  
  -- Weather/conditions
  reserve_day_utc TEXT,
  weather_conditions TEXT,
  pitch_report TEXT,
  toss_delayed_mins INTEGER DEFAULT 0,
  
  -- Result
  result_type TEXT, -- "WIN", "TIE", "NO_RESULT", "DRAW", "ABANDONED"
  winner_team_id INTEGER REFERENCES team(id),
  win_margin_runs INTEGER,
  win_margin_wickets INTEGER,
  win_method TEXT, -- "DLS", "VJD", "SUPER_OVER"
  
  notes TEXT,
  created_at_utc TEXT NOT NULL
);

CREATE TABLE match_team (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  team_id INTEGER NOT NULL REFERENCES team(id) ON DELETE RESTRICT,
  is_home BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE(match_id, team_id)
);

CREATE TABLE match_official (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  official_id INTEGER NOT NULL REFERENCES official(id),
  role TEXT NOT NULL, -- "FIELD_UMPIRE", "TV_UMPIRE", "MATCH_REFEREE" 
  UNIQUE(match_id, official_id)
);

CREATE TABLE match_toss (
  match_id INTEGER PRIMARY KEY REFERENCES match(id) ON DELETE CASCADE,
  won_by_team_id INTEGER NOT NULL REFERENCES team(id),
  decision_id INTEGER NOT NULL REFERENCES enum_toss_decision(id),
  delayed_start_mins INTEGER DEFAULT 0,
  toss_time_utc TEXT NOT NULL
);

-- Squad selection and playing XI
CREATE TABLE match_player (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  team_id INTEGER NOT NULL REFERENCES team(id),
  player_id INTEGER NOT NULL REFERENCES player(id),
  
  -- Squad roles
  is_playing_xi BOOLEAN NOT NULL DEFAULT TRUE,
  is_substitute BOOLEAN NOT NULL DEFAULT FALSE,
  is_captain BOOLEAN NOT NULL DEFAULT FALSE,
  is_wicketkeeper BOOLEAN NOT NULL DEFAULT FALSE,
  is_vice_captain BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Batting order (1-11 for XI, NULL for substitutes)
  batting_order INTEGER,
  
  -- Substitute info
  substitute_for_player_id INTEGER REFERENCES player(id),
  
  UNIQUE(match_id, player_id),
  UNIQUE(match_id, team_id, batting_order) -- No duplicate batting positions
);

CREATE TABLE innings (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  seq_number INTEGER NOT NULL, -- 1,2,3,4 for follow-on matches
  batting_team_id INTEGER NOT NULL REFERENCES team(id),
  bowling_team_id INTEGER NOT NULL REFERENCES team(id),
  
  -- Innings state
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  follow_on BOOLEAN NOT NULL DEFAULT FALSE,
  declared BOOLEAN NOT NULL DEFAULT FALSE,
  forfeited BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Targets (for chases and DLS)
  target_runs INTEGER, -- NULL for first innings
  target_balls INTEGER, -- for DLS shortened games
  
  -- Timing
  start_time_utc TEXT,
  end_time_utc TEXT,
  
  UNIQUE(match_id, seq_number)
);

-- DLS revision tracking  
CREATE TABLE dls_revision (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id),
  innings_id INTEGER NOT NULL REFERENCES innings(id),
  revision_time_utc TEXT NOT NULL,
  at_over INTEGER NOT NULL,
  at_ball INTEGER NOT NULL,
  wickets_fallen INTEGER NOT NULL,
  resources_team_a REAL NOT NULL, -- percentage 0-100
  resources_team_b REAL NOT NULL,
  par_score INTEGER,
  revised_target INTEGER,
  method_version TEXT NOT NULL, -- "D/L Standard", "D/L Stern"
  interruption_reason TEXT NOT NULL -- "RAIN", "BAD_LIGHT", "WET_OUTFIELD"
);

-- Ball-by-ball delivery records (source of truth)
CREATE TABLE delivery (
  id INTEGER PRIMARY KEY,
  public_id TEXT UNIQUE NOT NULL,
  innings_id INTEGER NOT NULL REFERENCES innings(id) ON DELETE CASCADE,
  
  -- Ball position in match
  over_number INTEGER NOT NULL, -- 0-based
  ball_in_over INTEGER NOT NULL, -- 1-6 (or 1-8 for 8-ball overs)
  is_legal_delivery BOOLEAN NOT NULL, -- FALSE for wides/no-balls
  
  -- Timing and sequence
  ts_utc TEXT NOT NULL,
  ball_sequence INTEGER NOT NULL, -- Global sequence in innings for ordering
  
  -- Players involved
  striker_id INTEGER NOT NULL REFERENCES player(id),
  non_striker_id INTEGER NOT NULL REFERENCES player(id), 
  bowler_id INTEGER NOT NULL REFERENCES player(id),
  wicketkeeper_id INTEGER REFERENCES player(id),
  
  -- Runs scored
  runs_batter INTEGER NOT NULL DEFAULT 0,
  runs_extras INTEGER NOT NULL DEFAULT 0,
  extra_type_id INTEGER REFERENCES enum_extra_type(id),
  
  -- Boundaries
  is_four BOOLEAN NOT NULL DEFAULT FALSE,
  is_six BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Dismissals
  wicket_type_id INTEGER REFERENCES enum_wicket_type(id),
  out_player_id INTEGER REFERENCES player(id),
  fielder_id INTEGER REFERENCES player(id), -- Catcher/runner-out fielder
  
  -- Analytics coordinates (0-100 normalized)
  wagon_x REAL, -- Shot direction for wagon wheel
  wagon_y REAL,
  pitch_x REAL, -- Ball pitching spot for pitch maps  
  pitch_y REAL,
  shot_zone TEXT, -- "FINE_LEG", "COVER", "STRAIGHT", etc.
  
  -- Commentary and match state
  commentary_text TEXT,
  ball_speed_kmh REAL,
  shot_power_rating INTEGER, -- 1-10 scale
  
  -- Non-destructive corrections
  replaces_delivery_id INTEGER REFERENCES delivery(id),
  is_superseded BOOLEAN NOT NULL DEFAULT FALSE,
  
  UNIQUE(innings_id, over_number, ball_in_over, COALESCE(replaces_delivery_id, 0))
);

-- Powerplay periods tracking
CREATE TABLE powerplay (
  id INTEGER PRIMARY KEY,
  innings_id INTEGER NOT NULL REFERENCES innings(id) ON DELETE CASCADE,
  powerplay_type TEXT NOT NULL, -- "MANDATORY", "BATTING", "BOWLING"  
  start_over INTEGER NOT NULL,
  end_over INTEGER NOT NULL,
  fielding_restrictions TEXT -- JSON describing field placement rules
);

-- Match interruptions (rain, bad light, etc.)
CREATE TABLE match_interruption (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  innings_id INTEGER REFERENCES innings(id),
  start_time_utc TEXT NOT NULL,
  end_time_utc TEXT,
  reason TEXT NOT NULL, -- "RAIN", "BAD_LIGHT", "WET_OUTFIELD", "CROWD_TROUBLE"
  overs_lost REAL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- PERFORMANCE INDEXES
CREATE INDEX idx_delivery_innings_over ON delivery(innings_id, over_number, ball_in_over);
CREATE INDEX idx_delivery_bowler ON delivery(bowler_id) WHERE wicket_type_id IS NOT NULL;
CREATE INDEX idx_delivery_striker ON delivery(striker_id);
CREATE INDEX idx_delivery_current ON delivery(innings_id, is_superseded, ball_sequence);
CREATE INDEX idx_delivery_boundaries ON delivery(innings_id) WHERE is_four = TRUE OR is_six = TRUE;

CREATE INDEX idx_match_tournament ON match(tournament_id, start_time_utc);
CREATE INDEX idx_match_team ON match_team(team_id, match_id);
CREATE INDEX idx_match_venue_date ON match(venue_id, start_time_utc);

CREATE INDEX idx_innings_match ON innings(match_id, seq_number);
CREATE INDEX idx_team_player_active ON team_player(team_id, player_id) WHERE end_date IS NULL;
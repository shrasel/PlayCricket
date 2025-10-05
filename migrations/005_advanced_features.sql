-- PlayCricket Platform - Advanced Features Migration 005
-- DRS events, live commentary, powerplay tracking, and match interruptions

-- =============================================================================
-- DRS (Decision Review System) EVENTS 
-- =============================================================================
CREATE TABLE drs_event (
  id INTEGER PRIMARY KEY,
  delivery_id INTEGER NOT NULL REFERENCES delivery(id) ON DELETE CASCADE,
  innings_id INTEGER NOT NULL REFERENCES innings(id),
  
  -- Review details
  reviewing_team_id INTEGER NOT NULL REFERENCES team(id),
  umpire_decision TEXT NOT NULL, -- "OUT", "NOT_OUT"
  drs_decision TEXT NOT NULL, -- "UPHELD", "OVERTURNED", "UMPIRES_CALL"
  
  -- Review type and technology
  review_type TEXT NOT NULL, -- "LBW", "CAUGHT", "RUN_OUT", "STUMPING"
  technology_used TEXT NOT NULL, -- "ULTRA_EDGE", "BALL_TRACKING", "HOT_SPOT"
  
  -- Tracking data (for LBW reviews)
  ball_tracking_data TEXT, -- JSON: pitch point, impact point, wicket prediction
  impact_inline BOOLEAN, -- Ball hitting in line with stumps
  impact_margin_mm REAL, -- Distance from wicket line
  hitting_stumps BOOLEAN, -- Would ball hit stumps
  wickets_missing_mm REAL, -- How far over stumps
  
  -- Audio/visual evidence
  ultra_edge_spike BOOLEAN DEFAULT FALSE,
  hot_spot_detected BOOLEAN DEFAULT FALSE,
  
  -- Review outcome
  reviews_remaining_batting INTEGER,
  reviews_remaining_bowling INTEGER,
  
  -- Timing
  review_requested_at TEXT NOT NULL,
  decision_made_at TEXT NOT NULL,
  
  notes TEXT
);

-- =============================================================================
-- LIVE COMMENTARY FEED
-- =============================================================================
CREATE TABLE commentary (
  id INTEGER PRIMARY KEY,
  delivery_id INTEGER REFERENCES delivery(id), -- NULL for general match commentary
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  innings_id INTEGER REFERENCES innings(id),
  
  -- Commentary content
  commentary_text TEXT NOT NULL,
  commentary_type TEXT NOT NULL, -- "BALL", "OVER", "WICKET", "BOUNDARY", "MILESTONE", "GENERAL"
  
  -- Timing and sequence
  timestamp_utc TEXT NOT NULL,
  sequence_number INTEGER NOT NULL, -- For ordering within match
  
  -- Metadata
  commentator_name TEXT,
  is_key_moment BOOLEAN DEFAULT FALSE,
  is_verified BOOLEAN DEFAULT TRUE,
  
  -- Social engagement (optional)
  likes_count INTEGER DEFAULT 0,
  
  UNIQUE(match_id, sequence_number)
);

-- =============================================================================
-- POWERPLAY DETAILED TRACKING
-- =============================================================================
-- Enhance existing powerplay table with more details
ALTER TABLE powerplay ADD COLUMN powerplay_number INTEGER; -- 1st, 2nd, 3rd powerplay
ALTER TABLE powerplay ADD COLUMN max_fielders_outside_circle INTEGER DEFAULT 2;
ALTER TABLE powerplay ADD COLUMN is_batting_powerplay BOOLEAN DEFAULT FALSE;
ALTER TABLE powerplay ADD COLUMN taken_by_team_id INTEGER REFERENCES team(id);

-- =============================================================================
-- PENALTY RUNS TRACKING
-- =============================================================================
CREATE TABLE penalty_runs (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id) ON DELETE CASCADE,
  innings_id INTEGER REFERENCES innings(id),
  delivery_id INTEGER REFERENCES delivery(id), -- NULL if awarded between deliveries
  
  -- Penalty details
  awarded_to_team_id INTEGER NOT NULL REFERENCES team(id),
  penalty_runs INTEGER NOT NULL,
  reason TEXT NOT NULL, -- "BALL_TAMPERING", "SLOW_OVER_RATE", "DANGEROUS_PLAY", "FIELD_PLACEMENT"
  
  -- Official who awarded penalty
  umpire_id INTEGER REFERENCES official(id),
  
  -- Timing
  awarded_at_utc TEXT NOT NULL,
  over_number INTEGER,
  ball_number INTEGER,
  
  notes TEXT
);

-- =============================================================================
-- MATCH INTERRUPTION DETAILED TRACKING  
-- =============================================================================
-- Enhance existing match_interruption table
ALTER TABLE match_interruption ADD COLUMN overs_scheduled INTEGER; -- Overs scheduled before interruption
ALTER TABLE match_interruption ADD COLUMN overs_remaining INTEGER; -- Overs left when play resumes
ALTER TABLE match_interruption ADD COLUMN dls_applied BOOLEAN DEFAULT FALSE;
ALTER TABLE match_interruption ADD COLUMN revised_target INTEGER; -- New target after DLS

-- =============================================================================
-- LIVE MATCH STATE TRACKING
-- =============================================================================
CREATE TABLE live_match_state (
  match_id INTEGER PRIMARY KEY REFERENCES match(id) ON DELETE CASCADE,
  
  -- Current state
  current_innings_id INTEGER REFERENCES innings(id),
  current_over INTEGER DEFAULT 0,
  current_ball INTEGER DEFAULT 1,
  
  -- Current players on field
  striker_id INTEGER REFERENCES player(id),
  non_striker_id INTEGER REFERENCES player(id),
  bowler_id INTEGER REFERENCES player(id),
  wicketkeeper_id INTEGER REFERENCES player(id),
  
  -- Match situation
  is_powerplay BOOLEAN DEFAULT FALSE,
  powerplay_type TEXT, -- "MANDATORY", "BATTING", "BOWLING"
  powerplay_end_over INTEGER,
  
  -- Required run rate (for chases)
  required_run_rate REAL,
  required_runs INTEGER,
  required_balls INTEGER,
  
  -- Live tracking flags
  is_drinks_break BOOLEAN DEFAULT FALSE,
  is_strategic_timeout BOOLEAN DEFAULT FALSE,
  is_rain_delay BOOLEAN DEFAULT FALSE,
  
  -- Last updated
  last_updated_utc TEXT NOT NULL,
  
  -- Broadcasting info
  is_live_streaming BOOLEAN DEFAULT FALSE,
  viewer_count INTEGER DEFAULT 0
);

-- =============================================================================
-- BOWLING SPELL TRACKING
-- =============================================================================
CREATE TABLE bowling_spell (
  id INTEGER PRIMARY KEY,
  innings_id INTEGER NOT NULL REFERENCES innings(id),
  bowler_id INTEGER NOT NULL REFERENCES player(id),
  
  -- Spell boundaries
  start_over INTEGER NOT NULL,
  end_over INTEGER, -- NULL for ongoing spell
  
  -- Spell statistics (computed from deliveries)
  overs_bowled REAL DEFAULT 0.0,
  runs_conceded INTEGER DEFAULT 0,
  wickets_taken INTEGER DEFAULT 0,
  maidens INTEGER DEFAULT 0,
  
  -- Spell context
  spell_number INTEGER NOT NULL, -- 1st spell, 2nd spell, etc.
  is_opening_spell BOOLEAN DEFAULT FALSE,
  is_death_spell BOOLEAN DEFAULT FALSE,
  
  UNIQUE(innings_id, bowler_id, spell_number)
);

-- =============================================================================
-- FIELD PLACEMENT TRACKING (optional advanced feature)
-- =============================================================================
CREATE TABLE field_placement (
  id INTEGER PRIMARY KEY,
  delivery_id INTEGER NOT NULL REFERENCES delivery(id),
  
  -- Fielder positions (normalized coordinates 0-100)
  fielder_id INTEGER NOT NULL REFERENCES player(id),
  position_name TEXT, -- "SLIP", "COVER", "MID_ON", "FINE_LEG"
  x_coordinate REAL, -- 0-100 across the field
  y_coordinate REAL, -- 0-100 up the pitch
  
  -- Fielding restrictions
  is_inside_circle BOOLEAN DEFAULT TRUE,
  is_catching_position BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- MILESTONE TRACKING
-- =============================================================================
CREATE TABLE milestone (
  id INTEGER PRIMARY KEY,
  delivery_id INTEGER REFERENCES delivery(id),
  match_id INTEGER NOT NULL REFERENCES match(id),
  player_id INTEGER REFERENCES player(id),
  team_id INTEGER REFERENCES team(id),
  
  -- Milestone details
  milestone_type TEXT NOT NULL, -- "FIFTY", "CENTURY", "FIFER", "HATTRICK", "TEAM_100", "TEAM_200"
  milestone_value INTEGER NOT NULL, -- 50, 100, 150, 200, etc.
  
  -- Context
  balls_taken INTEGER, -- Balls to reach milestone
  milestone_ball_id INTEGER REFERENCES delivery(id), -- Specific ball that achieved it
  
  -- Timing
  achieved_at_utc TEXT NOT NULL,
  
  -- Celebration/acknowledgment
  was_celebrated BOOLEAN DEFAULT FALSE,
  celebration_description TEXT
);

-- =============================================================================
-- SUPER OVER TRACKING (for tied matches)
-- =============================================================================
CREATE TABLE super_over (
  id INTEGER PRIMARY KEY,
  match_id INTEGER NOT NULL REFERENCES match(id),
  
  -- Super over details
  batting_first_team_id INTEGER NOT NULL REFERENCES team(id),
  bowling_first_team_id INTEGER NOT NULL REFERENCES team(id),
  
  -- Results
  team1_runs INTEGER DEFAULT 0,
  team1_wickets INTEGER DEFAULT 0,
  team2_runs INTEGER DEFAULT 0,
  team2_wickets INTEGER DEFAULT 0,
  
  winner_team_id INTEGER REFERENCES team(id),
  
  -- Special cases
  is_multiple_super_over BOOLEAN DEFAULT FALSE,
  super_over_number INTEGER DEFAULT 1,
  
  created_at_utc TEXT NOT NULL
);

-- =============================================================================
-- ENHANCED VIEWS FOR ADVANCED FEATURES
-- =============================================================================

-- Live match center view (real-time data for UI)
CREATE VIEW v_live_match_center AS
SELECT 
  m.id as match_id,
  m.public_id,
  lms.current_innings_id,
  lms.current_over,
  lms.current_ball,
  
  -- Current players
  striker.known_as as current_striker,
  non_striker.known_as as current_non_striker,
  bowler.known_as as current_bowler,
  
  -- Match situation
  lms.is_powerplay,
  lms.powerplay_type,
  lms.required_run_rate,
  lms.required_runs,
  lms.required_balls,
  
  -- Current innings summary
  vis.total_runs,
  vis.wickets_fallen,
  vis.current_run_rate,
  vis.target_runs,
  
  -- Recent deliveries (last 6 balls)
  (SELECT GROUP_CONCAT(
    CASE 
      WHEN d.runs_batter = 0 AND d.extra_type_id IS NULL THEN '•'
      WHEN d.is_four THEN '4'
      WHEN d.is_six THEN '6'
      WHEN d.extra_type_id IS NOT NULL THEN 'W'
      ELSE CAST(d.runs_batter + d.runs_extras AS TEXT)
    END, ' '
   )
   FROM (
     SELECT * FROM v_current_deliveries 
     WHERE innings_id = lms.current_innings_id
     ORDER BY ball_sequence DESC
     LIMIT 6
   ) d
  ) as recent_balls,
  
  -- Match status
  ms.description as match_status,
  lms.last_updated_utc

FROM match m
JOIN live_match_state lms ON m.id = lms.match_id
LEFT JOIN player striker ON lms.striker_id = striker.id
LEFT JOIN player non_striker ON lms.non_striker_id = non_striker.id
LEFT JOIN player bowler ON lms.bowler_id = bowler.id
LEFT JOIN v_innings_summary vis ON lms.current_innings_id = vis.innings_id
LEFT JOIN enum_match_status ms ON m.status_id = ms.id;

-- Recent commentary view
CREATE VIEW v_recent_commentary AS
SELECT 
  c.id,
  c.match_id,
  c.commentary_text,
  c.commentary_type,
  c.timestamp_utc,
  c.is_key_moment,
  
  -- Delivery context if available
  d.over_number,
  d.ball_in_over,
  d.runs_batter + d.runs_extras as runs_scored,
  
  -- Player context
  striker.known_as as striker_name,
  bowler.known_as as bowler_name

FROM commentary c
LEFT JOIN delivery d ON c.delivery_id = d.id
LEFT JOIN player striker ON d.striker_id = striker.id
LEFT JOIN player bowler ON d.bowler_id = bowler.id
ORDER BY c.match_id, c.sequence_number DESC;

-- Current bowling spell view
CREATE VIEW v_current_bowling_spell AS
SELECT 
  bs.id,
  bs.innings_id,
  bs.bowler_id,
  p.known_as as bowler_name,
  bs.start_over,
  bs.spell_number,
  
  -- Real-time spell stats from deliveries
  COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) as balls_bowled,
  SUM(d.runs_batter + d.runs_extras) as runs_conceded,
  COUNT(CASE WHEN d.wicket_type_id IS NOT NULL THEN 1 END) as wickets_taken,
  
  -- Economy in current spell
  CASE 
    WHEN COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) > 0
    THEN ROUND(CAST(SUM(d.runs_batter + d.runs_extras) AS REAL) * 6.0 / COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END), 2)
    ELSE 0.0
  END as current_economy

FROM bowling_spell bs
JOIN player p ON bs.bowler_id = p.id
LEFT JOIN v_current_deliveries d ON bs.innings_id = d.innings_id 
                                 AND bs.bowler_id = d.bowler_id
                                 AND d.over_number >= bs.start_over
                                 AND (bs.end_over IS NULL OR d.over_number <= bs.end_over)
WHERE bs.end_over IS NULL -- Only current/ongoing spells
GROUP BY bs.id, bs.innings_id, bs.bowler_id, p.known_as, bs.start_over, bs.spell_number;

-- =============================================================================
-- PERFORMANCE INDEXES FOR LIVE FEATURES
-- =============================================================================
CREATE INDEX idx_commentary_match_sequence ON commentary(match_id, sequence_number DESC);
CREATE INDEX idx_live_state_match ON live_match_state(match_id);
CREATE INDEX idx_drs_delivery ON drs_event(delivery_id);
CREATE INDEX idx_milestone_player ON milestone(player_id, milestone_type);
CREATE INDEX idx_bowling_spell_active ON bowling_spell(innings_id, bowler_id) WHERE end_over IS NULL;
-- PlayCricket Platform - Statistics Views Migration 003
-- Core views for scorecards, partnerships, Manhattan chart, and wagon wheel analytics

-- =============================================================================
-- CURRENT DELIVERIES VIEW (filters out superseded corrections)
-- =============================================================================
CREATE VIEW v_current_deliveries AS
SELECT 
  d.*,
  mt.code as match_type,
  et.code as extra_type,
  wt.code as wicket_type,
  striker.known_as as striker_name,
  non_striker.known_as as non_striker_name,
  bowler.known_as as bowler_name,
  out_player.known_as as out_player_name,
  fielder.known_as as fielder_name
FROM delivery d
JOIN innings i ON d.innings_id = i.id
JOIN match m ON i.match_id = m.id
JOIN enum_match_type mt ON m.match_type_id = mt.id
LEFT JOIN enum_extra_type et ON d.extra_type_id = et.id
LEFT JOIN enum_wicket_type wt ON d.wicket_type_id = wt.id
LEFT JOIN player striker ON d.striker_id = striker.id
LEFT JOIN player non_striker ON d.non_striker_id = non_striker.id
LEFT JOIN player bowler ON d.bowler_id = bowler.id
LEFT JOIN player out_player ON d.out_player_id = out_player.id
LEFT JOIN player fielder ON d.fielder_id = fielder.id
WHERE d.is_superseded = FALSE;

-- =============================================================================
-- INNINGS SUMMARY VIEW (computed totals from deliveries)
-- =============================================================================
CREATE VIEW v_innings_summary AS
SELECT 
  i.id as innings_id,
  i.public_id,
  i.match_id,
  i.seq_number,
  i.batting_team_id,
  i.bowling_team_id,
  i.target_runs,
  
  -- Computed totals from deliveries
  COALESCE(SUM(d.runs_batter + d.runs_extras), 0) as total_runs,
  COALESCE(COUNT(CASE WHEN d.wicket_type_id IS NOT NULL AND wt.code NOT IN ('RETIRED_HURT', 'RETIRED_NOT_OUT') THEN 1 END), 0) as wickets_fallen,
  COALESCE(COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END), 0) as legal_balls_faced,
  
  -- Overs calculation  
  COALESCE(MAX(d.over_number), 0) as overs_completed,
  COALESCE(COUNT(CASE WHEN d.is_legal_delivery = TRUE AND d.over_number = MAX(d.over_number) THEN 1 END), 0) as balls_in_current_over,
  
  -- Boundaries
  COALESCE(COUNT(CASE WHEN d.is_four = TRUE THEN 1 END), 0) as fours,
  COALESCE(COUNT(CASE WHEN d.is_six = TRUE THEN 1 END), 0) as sixes,
  
  -- Extras breakdown
  COALESCE(SUM(CASE WHEN et.code = 'BYE' THEN d.runs_extras ELSE 0 END), 0) as byes,
  COALESCE(SUM(CASE WHEN et.code = 'LEGBYE' THEN d.runs_extras ELSE 0 END), 0) as leg_byes,
  COALESCE(SUM(CASE WHEN et.code = 'WIDE' THEN d.runs_extras ELSE 0 END), 0) as wides,
  COALESCE(SUM(CASE WHEN et.code = 'NO_BALL' THEN d.runs_extras ELSE 0 END), 0) as no_balls,
  COALESCE(SUM(CASE WHEN et.code = 'PENALTY' THEN d.runs_extras ELSE 0 END), 0) as penalties,
  
  -- Current run rate
  CASE 
    WHEN COALESCE(COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END), 0) > 0 
    THEN ROUND(CAST(COALESCE(SUM(d.runs_batter + d.runs_extras), 0) AS REAL) * 6.0 / COALESCE(COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END), 1), 2)
    ELSE 0.0 
  END as current_run_rate,
  
  -- Status flags
  i.is_completed,
  i.declared,
  i.forfeited,
  
  -- Timing
  i.start_time_utc,
  i.end_time_utc

FROM innings i
LEFT JOIN v_current_deliveries d ON i.id = d.innings_id
LEFT JOIN enum_extra_type et ON d.extra_type_id = et.id
LEFT JOIN enum_wicket_type wt ON d.wicket_type_id = wt.id
GROUP BY i.id, i.public_id, i.match_id, i.seq_number, i.batting_team_id, i.bowling_team_id, 
         i.target_runs, i.is_completed, i.declared, i.forfeited, i.start_time_utc, i.end_time_utc;

-- =============================================================================
-- BATTING SCORECARD VIEW  
-- =============================================================================
CREATE VIEW v_batting_scorecard AS
WITH batsman_stats AS (
  SELECT 
    d.innings_id,
    d.striker_id as player_id,
    SUM(d.runs_batter) as runs_scored,
    COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) as balls_faced,
    COUNT(CASE WHEN d.is_four = TRUE THEN 1 END) as fours,
    COUNT(CASE WHEN d.is_six = TRUE THEN 1 END) as sixes,
    
    -- Dismissal info (only the final dismissal if multiple corrections)
    MAX(CASE WHEN d.wicket_type_id IS NOT NULL AND d.out_player_id = d.striker_id THEN d.id END) as dismissal_delivery_id
    
  FROM v_current_deliveries d
  GROUP BY d.innings_id, d.striker_id
),
dismissal_details AS (
  SELECT 
    d.id as delivery_id,
    d.out_player_id as player_id,
    wt.description as dismissal_type,
    bowler.known_as as bowler_name,
    fielder.known_as as fielder_name
  FROM v_current_deliveries d
  JOIN enum_wicket_type wt ON d.wicket_type_id = wt.id
  LEFT JOIN player bowler ON d.bowler_id = bowler.id
  LEFT JOIN player fielder ON d.fielder_id = fielder.id
  WHERE d.wicket_type_id IS NOT NULL
)
SELECT 
  bs.innings_id,
  bs.player_id,
  p.known_as as player_name,
  mp.batting_order,
  mp.is_captain,
  mp.is_wicketkeeper,
  
  -- Batting figures
  bs.runs_scored,
  bs.balls_faced,
  bs.fours,
  bs.sixes,
  
  -- Strike rate
  CASE 
    WHEN bs.balls_faced > 0 
    THEN ROUND(CAST(bs.runs_scored AS REAL) * 100.0 / bs.balls_faced, 2)
    ELSE NULL 
  END as strike_rate,
  
  -- Dismissal info
  CASE 
    WHEN bs.dismissal_delivery_id IS NOT NULL THEN dd.dismissal_type
    WHEN bs.runs_scored > 0 OR bs.balls_faced > 0 THEN 'not out'
    ELSE 'did not bat'
  END as dismissal_info,
  
  dd.bowler_name as dismissed_by_bowler,
  dd.fielder_name as dismissed_by_fielder

FROM batsman_stats bs
JOIN player p ON bs.player_id = p.id
JOIN innings i ON bs.innings_id = i.id
JOIN match_player mp ON i.match_id = mp.match_id AND bs.player_id = mp.player_id 
LEFT JOIN dismissal_details dd ON bs.dismissal_delivery_id = dd.delivery_id

WHERE bs.runs_scored > 0 OR bs.balls_faced > 0 OR bs.dismissal_delivery_id IS NOT NULL
ORDER BY bs.innings_id, mp.batting_order;

-- =============================================================================
-- BOWLING FIGURES VIEW
-- =============================================================================
CREATE VIEW v_bowling_figures AS
SELECT 
  d.innings_id,
  d.bowler_id as player_id,
  p.known_as as bowler_name,
  
  -- Overs bowled calculation
  COUNT(DISTINCT d.over_number) as overs_completed,
  COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) as legal_balls_bowled,
  
  -- Format overs as "15.4" style
  CAST(COUNT(DISTINCT d.over_number) AS TEXT) || '.' || 
  CAST(COUNT(CASE WHEN d.is_legal_delivery = TRUE AND d.over_number = MAX(d.over_number) THEN 1 END) AS TEXT) as overs_bowled,
  
  -- Maiden overs (overs with 0 runs)
  COUNT(CASE 
    WHEN over_runs.runs_in_over = 0 AND over_runs.legal_balls = 6 THEN 1 
  END) as maidens,
  
  -- Runs conceded and wickets
  SUM(d.runs_batter + d.runs_extras) as runs_conceded,
  COUNT(CASE WHEN d.wicket_type_id IS NOT NULL AND wt.code NOT IN ('RETIRED_HURT', 'RETIRED_NOT_OUT') THEN 1 END) as wickets,
  
  -- Economy rate
  CASE 
    WHEN COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) > 0
    THEN ROUND(CAST(SUM(d.runs_batter + d.runs_extras) AS REAL) * 6.0 / COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END), 2)
    ELSE 0.0
  END as economy_rate,
  
  -- Additional stats
  COUNT(CASE WHEN d.is_four = TRUE THEN 1 END) as fours_conceded,
  COUNT(CASE WHEN d.is_six = TRUE THEN 1 END) as sixes_conceded,
  COUNT(CASE WHEN et.code = 'WIDE' THEN 1 END) as wides,
  COUNT(CASE WHEN et.code = 'NO_BALL' THEN 1 END) as no_balls

FROM v_current_deliveries d
JOIN player p ON d.bowler_id = p.id
LEFT JOIN enum_wicket_type wt ON d.wicket_type_id = wt.id
LEFT JOIN enum_extra_type et ON d.extra_type_id = et.id
LEFT JOIN (
  -- Subquery to calculate runs per over for maiden detection
  SELECT 
    innings_id,
    bowler_id,
    over_number,
    SUM(runs_batter + runs_extras) as runs_in_over,
    COUNT(CASE WHEN is_legal_delivery = TRUE THEN 1 END) as legal_balls
  FROM v_current_deliveries
  GROUP BY innings_id, bowler_id, over_number
) over_runs ON d.innings_id = over_runs.innings_id 
             AND d.bowler_id = over_runs.bowler_id 
             AND d.over_number = over_runs.over_number

GROUP BY d.innings_id, d.bowler_id, p.known_as
ORDER BY d.innings_id, SUM(d.runs_batter + d.runs_extras) ASC;

-- =============================================================================
-- PARTNERSHIPS VIEW
-- =============================================================================
CREATE VIEW v_partnerships AS
WITH partnership_boundaries AS (
  -- Find when partnerships start and end (wickets or innings end)
  SELECT 
    d.innings_id,
    d.striker_id,
    d.non_striker_id,
    d.ball_sequence as start_sequence,
    LEAD(d.ball_sequence, 1, 999999) OVER (
      PARTITION BY d.innings_id 
      ORDER BY d.ball_sequence
    ) as end_sequence
  FROM v_current_deliveries d
  WHERE d.wicket_type_id IS NOT NULL 
     OR d.ball_sequence = (SELECT MAX(ball_sequence) FROM v_current_deliveries d2 WHERE d2.innings_id = d.innings_id)
),
partnership_details AS (
  SELECT 
    d.innings_id,
    pb.striker_id,
    pb.non_striker_id,
    SUM(d.runs_batter) as partnership_runs,
    COUNT(CASE WHEN d.is_legal_delivery = TRUE THEN 1 END) as balls_faced,
    COUNT(CASE WHEN d.is_four = TRUE THEN 1 END) as fours,
    COUNT(CASE WHEN d.is_six = TRUE THEN 1 END) as sixes,
    
    -- Individual contributions  
    SUM(CASE WHEN d.striker_id = pb.striker_id THEN d.runs_batter ELSE 0 END) as batsman1_runs,
    SUM(CASE WHEN d.striker_id = pb.non_striker_id THEN d.runs_batter ELSE 0 END) as batsman2_runs,
    
    ROW_NUMBER() OVER (PARTITION BY d.innings_id ORDER BY pb.start_sequence) as partnership_number
    
  FROM partnership_boundaries pb
  JOIN v_current_deliveries d ON d.innings_id = pb.innings_id
    AND d.ball_sequence >= pb.start_sequence 
    AND d.ball_sequence < pb.end_sequence
  GROUP BY d.innings_id, pb.striker_id, pb.non_striker_id, pb.start_sequence
)
SELECT 
  pd.innings_id,
  pd.partnership_number,
  p1.known_as as batsman1_name,
  p2.known_as as batsman2_name,
  pd.partnership_runs,
  pd.balls_faced,
  pd.fours,
  pd.sixes,
  pd.batsman1_runs,
  pd.batsman2_runs,
  
  -- Partnership strike rate
  CASE 
    WHEN pd.balls_faced > 0 
    THEN ROUND(CAST(pd.partnership_runs AS REAL) * 100.0 / pd.balls_faced, 2)
    ELSE 0.0 
  END as partnership_strike_rate

FROM partnership_details pd
JOIN player p1 ON pd.striker_id = p1.id
JOIN player p2 ON pd.non_striker_id = p2.id
ORDER BY pd.innings_id, pd.partnership_number;

-- =============================================================================
-- MANHATTAN CHART VIEW (over-by-over runs)
-- =============================================================================
CREATE VIEW v_manhattan_chart AS
SELECT 
  d.innings_id,
  d.over_number,
  SUM(d.runs_batter + d.runs_extras) as runs_in_over,
  SUM(SUM(d.runs_batter + d.runs_extras)) OVER (
    PARTITION BY d.innings_id 
    ORDER BY d.over_number 
    ROWS UNBOUNDED PRECEDING
  ) as cumulative_runs,
  COUNT(CASE WHEN d.wicket_type_id IS NOT NULL THEN 1 END) as wickets_in_over,
  SUM(COUNT(CASE WHEN d.wicket_type_id IS NOT NULL THEN 1 END)) OVER (
    PARTITION BY d.innings_id 
    ORDER BY d.over_number 
    ROWS UNBOUNDED PRECEDING
  ) as cumulative_wickets,
  
  -- Run rate for this over and cumulative
  ROUND(CAST(SUM(d.runs_batter + d.runs_extras) AS REAL), 2) as over_run_rate,
  ROUND(
    CAST(SUM(SUM(d.runs_batter + d.runs_extras)) OVER (
      PARTITION BY d.innings_id 
      ORDER BY d.over_number 
      ROWS UNBOUNDED PRECEDING
    ) AS REAL) / (d.over_number + 1), 2
  ) as cumulative_run_rate

FROM v_current_deliveries d
GROUP BY d.innings_id, d.over_number
ORDER BY d.innings_id, d.over_number;

-- =============================================================================
-- WAGON WHEEL VIEW (shot distribution)
-- =============================================================================
CREATE VIEW v_wagon_wheel AS
SELECT 
  d.innings_id,
  d.striker_id as player_id,
  p.known_as as player_name,
  
  -- Shot coordinates and details
  d.wagon_x,
  d.wagon_y, 
  d.runs_batter,
  d.is_four,
  d.is_six,
  d.shot_zone,
  
  -- Shot classification
  CASE 
    WHEN d.is_six = TRUE THEN 'SIX'
    WHEN d.is_four = TRUE THEN 'FOUR'
    WHEN d.runs_batter >= 2 THEN 'MULTIPLE'
    WHEN d.runs_batter = 1 THEN 'SINGLE'
    ELSE 'DOT'
  END as shot_type,
  
  -- Over context
  d.over_number,
  d.ball_in_over

FROM v_current_deliveries d
JOIN player p ON d.striker_id = p.id
WHERE d.wagon_x IS NOT NULL 
  AND d.wagon_y IS NOT NULL
  AND d.runs_batter >= 0
ORDER BY d.innings_id, d.striker_id, d.ball_sequence;

-- =============================================================================
-- MATCH SCORECARD SUMMARY VIEW
-- =============================================================================
CREATE VIEW v_match_scorecard AS
SELECT 
  m.id as match_id,
  m.public_id as match_public_id,
  m.status_id,
  ms.description as match_status,
  
  -- Teams
  t1.name as team1_name,
  t2.name as team2_name,
  
  -- Match details
  v.name as venue_name,
  m.start_time_utc,
  m.result_type,
  m.winner_team_id,
  m.win_margin_runs,
  m.win_margin_wickets,
  m.win_method,
  
  -- Toss
  tt.name as toss_winner,
  td.description as toss_decision,
  
  -- Innings summaries
  i1.total_runs as team1_runs,
  i1.wickets_fallen as team1_wickets,
  i1.overs_completed as team1_overs,
  i1.current_run_rate as team1_run_rate,
  
  i2.total_runs as team2_runs,
  i2.wickets_fallen as team2_wickets,
  i2.overs_completed as team2_overs,
  i2.current_run_rate as team2_run_rate,
  i2.target_runs as target_runs

FROM match m
JOIN enum_match_status ms ON m.status_id = ms.id
JOIN match_team mt1 ON m.id = mt1.match_id AND mt1.is_home = TRUE
JOIN match_team mt2 ON m.id = mt2.match_id AND mt2.is_home = FALSE
JOIN team t1 ON mt1.team_id = t1.id
JOIN team t2 ON mt2.team_id = t2.id
JOIN venue v ON m.venue_id = v.id
LEFT JOIN match_toss toss ON m.id = toss.match_id
LEFT JOIN team tt ON toss.won_by_team_id = tt.id
LEFT JOIN enum_toss_decision td ON toss.decision_id = td.id
LEFT JOIN v_innings_summary i1 ON m.id = i1.match_id AND i1.seq_number = 1
LEFT JOIN v_innings_summary i2 ON m.id = i2.match_id AND i2.seq_number = 2;

-- =============================================================================
-- PERFORMANCE INDEXES FOR VIEWS
-- =============================================================================
CREATE INDEX idx_delivery_striker_innings ON delivery(striker_id, innings_id) WHERE is_superseded = FALSE;
CREATE INDEX idx_delivery_bowler_innings ON delivery(bowler_id, innings_id) WHERE is_superseded = FALSE;
CREATE INDEX idx_delivery_wagon_coords ON delivery(innings_id) WHERE wagon_x IS NOT NULL AND wagon_y IS NOT NULL;
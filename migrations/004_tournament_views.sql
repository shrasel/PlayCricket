-- PlayCricket Platform - Tournament & League Tables Migration 004
-- Tournament standings, points calculation, and Net Run Rate (NRR) computation

-- =============================================================================
-- TEAM MATCH RESULTS VIEW (basis for league calculations)
-- =============================================================================
CREATE VIEW v_team_match_results AS
WITH match_results AS (
  SELECT 
    m.id as match_id,
    m.public_id as match_public_id,
    m.tournament_id,
    m.stage_id,
    m.result_type,
    m.winner_team_id,
    
    -- Team identification
    mt1.team_id as team1_id,
    mt2.team_id as team2_id,
    t1.name as team1_name,
    t2.name as team2_name,
    
    -- Innings totals for NRR calculation
    i1.total_runs as team1_runs,
    i1.legal_balls_faced as team1_balls,
    i2.total_runs as team2_runs, 
    i2.legal_balls_faced as team2_balls,
    
    -- Match format
    m.overs_limit,
    mt.code as match_type
    
  FROM match m
  JOIN match_team mt1 ON m.id = mt1.match_id AND mt1.is_home = TRUE
  JOIN match_team mt2 ON m.id = mt2.match_id AND mt2.is_home = FALSE
  JOIN team t1 ON mt1.team_id = t1.id
  JOIN team t2 ON mt2.team_id = t2.id
  JOIN enum_match_type mt ON m.match_type_id = mt.id
  LEFT JOIN v_innings_summary i1 ON m.id = i1.match_id AND i1.batting_team_id = t1.id
  LEFT JOIN v_innings_summary i2 ON m.id = i2.match_id AND i2.batting_team_id = t2.id
  
  WHERE m.result_type IN ('WIN', 'TIE', 'NO_RESULT')
    AND m.tournament_id IS NOT NULL
)
-- Flatten to one row per team per match
SELECT 
  mr.match_id,
  mr.match_public_id,
  mr.tournament_id,
  mr.stage_id,
  mr.match_type,
  mr.overs_limit,
  
  -- Team perspective
  mr.team1_id as team_id,
  mr.team1_name as team_name,
  mr.team2_id as opponent_id,
  mr.team2_name as opponent_name,
  
  -- Match result from team perspective
  CASE 
    WHEN mr.result_type = 'WIN' AND mr.winner_team_id = mr.team1_id THEN 'WON'
    WHEN mr.result_type = 'WIN' AND mr.winner_team_id = mr.team2_id THEN 'LOST'
    WHEN mr.result_type = 'TIE' THEN 'TIED'
    WHEN mr.result_type = 'NO_RESULT' THEN 'NO_RESULT'
    ELSE 'NO_RESULT'
  END as result,
  
  -- Runs scored/conceded
  mr.team1_runs as runs_for,
  mr.team1_balls as balls_for,
  mr.team2_runs as runs_against,
  mr.team2_balls as balls_against

FROM match_results mr

UNION ALL

SELECT 
  mr.match_id,
  mr.match_public_id,
  mr.tournament_id,
  mr.stage_id,
  mr.match_type,
  mr.overs_limit,
  
  -- Team 2 perspective
  mr.team2_id as team_id,
  mr.team2_name as team_name,
  mr.team1_id as opponent_id,
  mr.team1_name as opponent_name,
  
  -- Match result from team 2 perspective  
  CASE 
    WHEN mr.result_type = 'WIN' AND mr.winner_team_id = mr.team2_id THEN 'WON'
    WHEN mr.result_type = 'WIN' AND mr.winner_team_id = mr.team1_id THEN 'LOST'
    WHEN mr.result_type = 'TIE' THEN 'TIED'
    WHEN mr.result_type = 'NO_RESULT' THEN 'NO_RESULT'
    ELSE 'NO_RESULT'
  END as result,
  
  -- Runs scored/conceded (from team 2 perspective)
  mr.team2_runs as runs_for,
  mr.team2_balls as balls_for,
  mr.team1_runs as runs_against,
  mr.team1_balls as balls_against

FROM match_results mr;

-- =============================================================================
-- NET RUN RATE CALCULATION VIEW
-- =============================================================================
CREATE VIEW v_team_nrr AS
SELECT 
  tmr.tournament_id,
  tmr.stage_id,
  tmr.team_id,
  tmr.team_name,
  
  -- Aggregate runs and overs
  SUM(tmr.runs_for) as total_runs_for,
  SUM(CAST(tmr.balls_for AS REAL) / 6.0) as total_overs_for,
  SUM(tmr.runs_against) as total_runs_against,
  SUM(CAST(tmr.balls_against AS REAL) / 6.0) as total_overs_against,
  
  -- Net Run Rate calculation
  CASE 
    WHEN SUM(tmr.balls_for) > 0 AND SUM(tmr.balls_against) > 0 THEN
      ROUND(
        (CAST(SUM(tmr.runs_for) AS REAL) / (CAST(SUM(tmr.balls_for) AS REAL) / 6.0)) -
        (CAST(SUM(tmr.runs_against) AS REAL) / (CAST(SUM(tmr.balls_against) AS REAL) / 6.0)),
        3
      )
    ELSE 0.0
  END as net_run_rate

FROM v_team_match_results tmr
WHERE tmr.result != 'NO_RESULT'
GROUP BY tmr.tournament_id, tmr.stage_id, tmr.team_id, tmr.team_name;

-- =============================================================================
-- LEAGUE TABLE/STANDINGS VIEW
-- =============================================================================
CREATE VIEW v_league_table AS
WITH team_standings AS (
  SELECT 
    tmr.tournament_id,
    tmr.stage_id,
    tmr.team_id,
    tmr.team_name,
    
    -- Match statistics
    COUNT(*) as matches_played,
    COUNT(CASE WHEN tmr.result = 'WON' THEN 1 END) as matches_won,
    COUNT(CASE WHEN tmr.result = 'LOST' THEN 1 END) as matches_lost,
    COUNT(CASE WHEN tmr.result = 'TIED' THEN 1 END) as matches_tied,
    COUNT(CASE WHEN tmr.result = 'NO_RESULT' THEN 1 END) as matches_no_result,
    
    -- Run aggregates for NRR
    SUM(tmr.runs_for) as total_runs_for,
    SUM(tmr.runs_against) as total_runs_against,
    
    -- Points calculation (customizable via tournament.points_system)
    -- Default: Win=2, Tie=1, No Result=1, Loss=0
    (COUNT(CASE WHEN tmr.result = 'WON' THEN 1 END) * 2) +
    (COUNT(CASE WHEN tmr.result = 'TIED' THEN 1 END) * 1) +
    (COUNT(CASE WHEN tmr.result = 'NO_RESULT' THEN 1 END) * 1) as points
    
  FROM v_team_match_results tmr
  GROUP BY tmr.tournament_id, tmr.stage_id, tmr.team_id, tmr.team_name
)
SELECT 
  ts.tournament_id,
  ts.stage_id,
  ts.team_id,
  ts.team_name,
  ts.matches_played,
  ts.matches_won,
  ts.matches_lost,
  ts.matches_tied,
  ts.matches_no_result,
  ts.points,
  
  -- Win percentage
  CASE 
    WHEN ts.matches_played > 0 
    THEN ROUND(CAST(ts.matches_won AS REAL) * 100.0 / ts.matches_played, 1)
    ELSE 0.0 
  END as win_percentage,
  
  -- Net Run Rate from dedicated view
  COALESCE(nrr.net_run_rate, 0.0) as net_run_rate,
  
  -- Qualification status (placeholder for later enhancement)
  'TBD' as qualification_status,
  
  -- Table position (ranked by points, then NRR)
  RANK() OVER (
    PARTITION BY ts.tournament_id, ts.stage_id 
    ORDER BY ts.points DESC, COALESCE(nrr.net_run_rate, 0.0) DESC, ts.matches_won DESC
  ) as position

FROM team_standings ts
LEFT JOIN v_team_nrr nrr ON ts.tournament_id = nrr.tournament_id 
                        AND ts.stage_id = nrr.stage_id 
                        AND ts.team_id = nrr.team_id
ORDER BY ts.tournament_id, ts.stage_id, position;

-- =============================================================================
-- HEAD-TO-HEAD RECORDS VIEW
-- =============================================================================
CREATE VIEW v_head_to_head AS
WITH h2h_results AS (
  SELECT 
    tmr.tournament_id,
    tmr.team_id,
    tmr.opponent_id,
    tmr.team_name,
    tmr.opponent_name,
    
    COUNT(*) as matches_played,
    COUNT(CASE WHEN tmr.result = 'WON' THEN 1 END) as matches_won,
    COUNT(CASE WHEN tmr.result = 'LOST' THEN 1 END) as matches_lost,
    COUNT(CASE WHEN tmr.result = 'TIED' THEN 1 END) as matches_tied,
    
    SUM(tmr.runs_for) as runs_for,
    SUM(tmr.runs_against) as runs_against,
    
    -- Last match result
    MAX(tmr.match_id) as latest_match_id
    
  FROM v_team_match_results tmr
  GROUP BY tmr.tournament_id, tmr.team_id, tmr.opponent_id, tmr.team_name, tmr.opponent_name
)
SELECT 
  h2h.tournament_id,
  h2h.team_id,
  h2h.team_name,
  h2h.opponent_id,
  h2h.opponent_name,
  h2h.matches_played,
  h2h.matches_won,
  h2h.matches_lost,
  h2h.matches_tied,
  
  -- Head-to-head record summary
  h2h.matches_won || '-' || h2h.matches_lost || 
  CASE WHEN h2h.matches_tied > 0 THEN '-' || h2h.matches_tied ELSE '' END as h2h_record,
  
  -- Win percentage in head-to-head
  CASE 
    WHEN h2h.matches_played > 0 
    THEN ROUND(CAST(h2h.matches_won AS REAL) * 100.0 / h2h.matches_played, 1)
    ELSE 0.0 
  END as h2h_win_percentage,
  
  -- Recent form indicator
  CASE 
    WHEN recent_result.result = 'WON' THEN 'W'
    WHEN recent_result.result = 'LOST' THEN 'L'
    WHEN recent_result.result = 'TIED' THEN 'T'
    ELSE 'N'
  END as last_result

FROM h2h_results h2h
LEFT JOIN v_team_match_results recent_result ON h2h.latest_match_id = recent_result.match_id 
                                             AND h2h.team_id = recent_result.team_id;

-- =============================================================================
-- TOURNAMENT SUMMARY VIEW
-- =============================================================================
CREATE VIEW v_tournament_summary AS
SELECT 
  t.id as tournament_id,
  t.public_id,
  t.name as tournament_name,
  t.season_label,
  mt.description as match_type,
  t.start_date,
  t.end_date,
  
  -- Tournament statistics
  COUNT(DISTINCT m.id) as total_matches,
  COUNT(DISTINCT tt.team_id) as total_teams,
  COUNT(DISTINCT ts.id) as total_stages,
  
  -- Match completion status
  COUNT(CASE WHEN ms.code = 'COMPLETED' THEN 1 END) as completed_matches,
  COUNT(CASE WHEN ms.code = 'LIVE' THEN 1 END) as live_matches,
  COUNT(CASE WHEN ms.code = 'SCHEDULED' THEN 1 END) as upcoming_matches,
  
  -- Current stage
  (SELECT ts2.name 
   FROM tournament_stage ts2 
   WHERE ts2.tournament_id = t.id 
   ORDER BY ts2.sort_order DESC 
   LIMIT 1) as current_stage,
   
  -- Points system
  t.points_system

FROM tournament t
JOIN enum_match_type mt ON t.match_type_id = mt.id
LEFT JOIN tournament_team tt ON t.id = tt.tournament_id
LEFT JOIN tournament_stage ts ON t.id = ts.tournament_id
LEFT JOIN match m ON t.id = m.tournament_id
LEFT JOIN enum_match_status ms ON m.status_id = ms.id
GROUP BY t.id, t.public_id, t.name, t.season_label, mt.description, 
         t.start_date, t.end_date, t.points_system;

-- =============================================================================
-- RECENT FORM VIEW (last 5 matches)
-- =============================================================================
CREATE VIEW v_recent_form AS
WITH ranked_matches AS (
  SELECT 
    tmr.*,
    ROW_NUMBER() OVER (
      PARTITION BY tmr.team_id, tmr.tournament_id 
      ORDER BY tmr.match_id DESC
    ) as match_rank
  FROM v_team_match_results tmr
  JOIN match m ON tmr.match_id = m.id
  WHERE m.result_type IN ('WIN', 'TIE', 'NO_RESULT')
)
SELECT 
  rm.tournament_id,
  rm.team_id,
  rm.team_name,
  
  -- Last 5 results as string
  GROUP_CONCAT(
    CASE 
      WHEN rm.result = 'WON' THEN 'W'
      WHEN rm.result = 'LOST' THEN 'L'
      WHEN rm.result = 'TIED' THEN 'T'
      ELSE 'N'
    END,
    ''
  ) as recent_form,
  
  -- Form statistics
  COUNT(CASE WHEN rm.result = 'WON' THEN 1 END) as recent_wins,
  COUNT(CASE WHEN rm.result = 'LOST' THEN 1 END) as recent_losses,
  COUNT(*) as recent_matches

FROM ranked_matches rm
WHERE rm.match_rank <= 5
GROUP BY rm.tournament_id, rm.team_id, rm.team_name;

-- =============================================================================
-- TOURNAMENT FIXTURES VIEW (upcoming matches)
-- =============================================================================
CREATE VIEW v_tournament_fixtures AS
SELECT 
  m.id as match_id,
  m.public_id as match_public_id,
  m.tournament_id,
  ts.name as stage_name,
  
  -- Teams
  t1.name as team1_name,
  t1.short_name as team1_short,
  t2.name as team2_name,
  t2.short_name as team2_short,
  
  -- Venue and timing
  v.name as venue_name,
  v.city as venue_city,
  m.start_time_utc,
  m.local_start_time,
  
  -- Match details
  mt.description as match_type,
  m.overs_limit,
  ms.description as match_status,
  
  -- Historical context
  h2h.h2h_record,
  lt1.position as team1_position,
  lt2.position as team2_position

FROM match m
JOIN match_team mt1 ON m.id = mt1.match_id AND mt1.is_home = TRUE
JOIN match_team mt2 ON m.id = mt2.match_id AND mt2.is_home = FALSE
JOIN team t1 ON mt1.team_id = t1.id
JOIN team t2 ON mt2.team_id = t2.id
JOIN venue v ON m.venue_id = v.id
JOIN enum_match_type mt ON m.match_type_id = mt.id
JOIN enum_match_status ms ON m.status_id = ms.id
LEFT JOIN tournament_stage ts ON m.stage_id = ts.id
LEFT JOIN v_head_to_head h2h ON m.tournament_id = h2h.tournament_id 
                             AND t1.id = h2h.team_id 
                             AND t2.id = h2h.opponent_id
LEFT JOIN v_league_table lt1 ON m.tournament_id = lt1.tournament_id 
                             AND t1.id = lt1.team_id
LEFT JOIN v_league_table lt2 ON m.tournament_id = lt2.tournament_id 
                             AND t2.id = lt2.team_id
                             
WHERE m.tournament_id IS NOT NULL
ORDER BY m.start_time_utc;
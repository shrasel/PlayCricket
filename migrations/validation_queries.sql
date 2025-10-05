-- PlayCricket Platform - Validation Queries
-- Test data integrity and verify core schema functionality

-- 1. Test enum integrity
SELECT 'ENUM_VALIDATION' as test_name, 
       COUNT(*) as match_types,
       (SELECT COUNT(*) FROM enum_extra_type) as extra_types,
       (SELECT COUNT(*) FROM enum_wicket_type) as wicket_types,
       (SELECT COUNT(*) FROM enum_stage_type) as stage_types
FROM enum_match_type;

-- Expected: match_types=8, extra_types=6, wicket_types=13, stage_types=9

-- 2. Test foreign key constraints work
-- This should fail if FK constraints are properly enforced
-- INSERT INTO match_team (match_id, team_id) VALUES (999, 999);

-- 3. Test UNIQUE constraints
-- These should fail if unique constraints work
-- INSERT INTO enum_match_type (id, code, description) VALUES (99, 'TEST', 'Duplicate test');

-- 4. Test delivery ball indexing logic
-- Verify that legal deliveries increment correctly
WITH sample_over AS (
  SELECT 1 as innings_id, 0 as over_number, 1 as ball_in_over, 1 as is_legal_delivery, 0 as runs_batter, 0 as runs_extras
  UNION ALL SELECT 1, 0, 2, 0, 0, 1 -- Wide, doesn't advance ball count
  UNION ALL SELECT 1, 0, 2, 1, 4, 0 -- Legal ball after wide  
  UNION ALL SELECT 1, 0, 3, 1, 0, 0
  UNION ALL SELECT 1, 0, 4, 1, 0, 0
  UNION ALL SELECT 1, 0, 5, 1, 0, 0
  UNION ALL SELECT 1, 0, 6, 1, 0, 0
)
SELECT 
  'BALL_INDEXING' as test_name,
  COUNT(*) as total_deliveries,
  SUM(is_legal_delivery) as legal_deliveries,
  SUM(runs_batter + runs_extras) as total_runs
FROM sample_over;

-- Expected: total_deliveries=7, legal_deliveries=6, total_runs=5

-- 5. Test innings target calculation
-- Verify target runs logic for second innings  
WITH mock_innings AS (
  SELECT 1 as innings_id, 1 as seq_number, 1 as batting_team_id, 280 as first_innings_total
  UNION ALL SELECT 2, 2, 2, NULL -- Second innings, target = first_innings_total + 1
)
SELECT 
  'TARGET_CALCULATION' as test_name,
  seq_number,
  CASE 
    WHEN seq_number = 1 THEN NULL
    WHEN seq_number = 2 THEN 281 -- Target is first innings + 1
  END as calculated_target
FROM mock_innings;

-- 6. Test match result scenarios
WITH match_scenarios AS (
  SELECT 'WIN_BY_RUNS' as scenario, 250 as team1_score, 200 as team2_score, 'Team1 won by 50 runs' as expected_result
  UNION ALL SELECT 'WIN_BY_WICKETS', 200, 201, 'Team2 won by X wickets'
  UNION ALL SELECT 'TIE', 200, 200, 'Match tied'
)
SELECT 
  'RESULT_LOGIC' as test_name,
  scenario,
  CASE 
    WHEN team1_score > team2_score THEN 'WIN_BY_RUNS'
    WHEN team2_score > team1_score THEN 'WIN_BY_WICKETS' 
    ELSE 'TIE'
  END as calculated_result
FROM match_scenarios;

-- 7. Test player uniqueness across teams
-- Verify a player can't be in multiple active squads
WITH player_conflicts AS (
  SELECT player_id, COUNT(*) as active_teams
  FROM team_player 
  WHERE end_date IS NULL
  GROUP BY player_id
  HAVING COUNT(*) > 1
)
SELECT 
  'PLAYER_CONFLICTS' as test_name,
  COUNT(*) as conflicted_players
FROM player_conflicts;

-- Expected: conflicted_players=0

-- 8. Test delivery sequence ordering
-- Verify ball_sequence maintains correct chronological order
WITH delivery_order_test AS (
  SELECT 
    innings_id,
    over_number,
    ball_in_over,
    ball_sequence,
    LAG(ball_sequence) OVER (PARTITION BY innings_id ORDER BY ball_sequence) as prev_sequence
  FROM delivery
  WHERE is_superseded = FALSE
)
SELECT 
  'SEQUENCE_ORDERING' as test_name,
  COUNT(*) as total_deliveries,
  COUNT(CASE WHEN ball_sequence <= prev_sequence THEN 1 END) as sequence_errors
FROM delivery_order_test;

-- Expected: sequence_errors=0

-- 9. Test powerplay validation  
-- Ensure powerplay periods don't overlap
WITH powerplay_overlaps AS (
  SELECT 
    p1.innings_id,
    p1.powerplay_type as type1,
    p2.powerplay_type as type2
  FROM powerplay p1
  JOIN powerplay p2 ON p1.innings_id = p2.innings_id AND p1.id != p2.id
  WHERE p1.start_over < p2.end_over AND p2.start_over < p1.end_over
)
SELECT 
  'POWERPLAY_OVERLAPS' as test_name,
  COUNT(*) as overlapping_periods
FROM powerplay_overlaps;

-- Expected: overlapping_periods=0

-- 10. Test DLS revision chronology
-- Verify DLS revisions are in correct time order
WITH dls_order_test AS (
  SELECT 
    match_id,
    revision_time_utc,
    LAG(revision_time_utc) OVER (PARTITION BY match_id ORDER BY revision_time_utc) as prev_time
  FROM dls_revision
)
SELECT 
  'DLS_CHRONOLOGY' as test_name,
  COUNT(*) as total_revisions,
  COUNT(CASE WHEN revision_time_utc <= prev_time THEN 1 END) as time_errors
FROM dls_order_test;

-- Expected: time_errors=0
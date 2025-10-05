-- PlayCricket Platform - Enum Seeds Migration 002
-- Populate reference/lookup tables with standard cricket values

-- Match Types
INSERT INTO enum_match_type (id, code, description) VALUES
(1, 'TEST', 'Test Match (5 days, unlimited overs)'),
(2, 'ODI', 'One Day International (50 overs)'),
(3, 'T20I', 'Twenty20 International (20 overs)'),
(4, 'T10', 'Ten10 (10 overs)'),
(5, 'LIST_A', 'List A Domestic (50 overs)'),
(6, 'T20', 'Twenty20 Domestic (20 overs)'),
(7, 'FIRST_CLASS', 'First Class (unlimited overs)'),
(8, 'THE_HUNDRED', 'The Hundred (100 balls)');

-- Extra Types  
INSERT INTO enum_extra_type (id, code, description) VALUES
(1, 'NONE', 'No extras'),
(2, 'BYE', 'Bye runs (missed by wicketkeeper)'),
(3, 'LEGBYE', 'Leg bye runs (off batsman body)'),
(4, 'WIDE', 'Wide ball'),
(5, 'NO_BALL', 'No ball (various reasons)'),
(6, 'PENALTY', 'Penalty runs (awarded by umpire)');

-- Wicket Types
INSERT INTO enum_wicket_type (id, code, description) VALUES
(1, 'BOWLED', 'Bowled (ball hits stumps)'),
(2, 'LBW', 'Leg Before Wicket'),
(3, 'CAUGHT', 'Caught by fielder'),
(4, 'CAUGHT_BEHIND', 'Caught by wicketkeeper'),
(5, 'STUMPED', 'Stumped by wicketkeeper'),
(6, 'RUN_OUT', 'Run out'),
(7, 'HIT_WICKET', 'Hit wicket'),
(8, 'OBSTRUCTING_FIELD', 'Obstructing the field'),
(9, 'HANDLED_BALL', 'Handled the ball'),
(10, 'TIMED_OUT', 'Timed out'),
(11, 'RETIRED_OUT', 'Retired out'),
(12, 'RETIRED_HURT', 'Retired hurt (not out)'),
(13, 'RETIRED_NOT_OUT', 'Retired not out');

-- Tournament Stage Types
INSERT INTO enum_stage_type (id, code, description) VALUES
(1, 'GROUP', 'Group/Pool stage (round robin)'),
(2, 'LEAGUE', 'League stage (all play all)'),  
(3, 'QUALIFIER', 'Qualifier match'),
(4, 'ELIMINATOR', 'Eliminator match'),
(5, 'SEMI_FINAL', 'Semi-final'),
(6, 'FINAL', 'Final'),
(7, 'PLAYOFF', 'Playoff match'),
(8, 'SUPER_OVER', 'Super Over'),
(9, 'WARMUP', 'Warm-up/Practice match');

-- Match Status
INSERT INTO enum_match_status (id, code, description) VALUES
(1, 'SCHEDULED', 'Match scheduled'),
(2, 'DELAYED', 'Match delayed'),
(3, 'LIVE', 'Match in progress'),
(4, 'INNINGS_BREAK', 'Between innings'),
(5, 'RAIN_DELAY', 'Interrupted by rain'),
(6, 'BAD_LIGHT', 'Stopped for bad light'),
(7, 'STUMPS', 'End of day play'),
(8, 'COMPLETED', 'Match completed'),
(9, 'ABANDONED', 'Match abandoned'),
(10, 'NO_RESULT', 'No result'),
(11, 'CANCELLED', 'Match cancelled');

-- Toss Decision
INSERT INTO enum_toss_decision (id, code, description) VALUES
(1, 'BAT', 'Elected to bat first'),
(2, 'BOWL', 'Elected to bowl first');

-- Player Roles
INSERT INTO enum_player_role (id, code, description) VALUES
(1, 'BATSMAN', 'Specialist batsman'),
(2, 'BOWLER', 'Specialist bowler'),
(3, 'ALL_ROUNDER', 'All-rounder'),
(4, 'WICKETKEEPER', 'Wicketkeeper'),
(5, 'WK_BATSMAN', 'Wicketkeeper-batsman');

-- Batting Styles
INSERT INTO enum_batting_style (id, code, description) VALUES
(1, 'RHB', 'Right-hand batsman'),
(2, 'LHB', 'Left-hand batsman');

-- Bowling Styles  
INSERT INTO enum_bowling_style (id, code, description) VALUES
(1, 'RF', 'Right-arm fast'),
(2, 'LF', 'Left-arm fast'),
(3, 'RFM', 'Right-arm fast-medium'),
(4, 'LFM', 'Left-arm fast-medium'),
(5, 'RM', 'Right-arm medium'),
(6, 'LM', 'Left-arm medium'),
(7, 'ROB', 'Right-arm off-break'),
(8, 'LOB', 'Left-arm off-break'),
(9, 'RLB', 'Right-arm leg-break'),
(10, 'LLB', 'Left-arm leg-break'),
(11, 'SLA', 'Slow left-arm orthodox'),
(12, 'LCH', 'Left-arm chinaman'),
(13, 'RLG', 'Right-arm leg-spin googly'),
(14, 'LLG', 'Left-arm leg-spin googly');
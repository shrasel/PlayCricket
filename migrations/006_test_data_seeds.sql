-- PlayCricket Platform - Test Data Seeds
-- Complete demo scenario: 2-over T20 match with toss, XIs, live deliveries

-- =============================================================================
-- SAMPLE TEAMS AND PLAYERS
-- =============================================================================

-- Teams
INSERT INTO team (id, public_id, name, short_name, country_code, primary_color, secondary_color, created_at_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8G1', 'Mumbai Indians', 'MI', 'IND', '#004BA0', '#D1AB3E', '2024-01-01T00:00:00Z'),
(2, '01HP8X9K2MQRE4Y7V5N2M3F8G2', 'Chennai Super Kings', 'CSK', 'IND', '#FDB913', '#00A651', '2024-01-01T00:00:00Z');

-- Officials
INSERT INTO official (id, public_id, full_name, country_code, role, created_at_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8O1', 'Nitin Menon', 'IND', 'UMPIRE', '2024-01-01T00:00:00Z'),
(2, '01HP8X9K2MQRE4Y7V5N2M3F8O2', 'Anil Chaudhary', 'IND', 'UMPIRE', '2024-01-01T00:00:00Z'),
(3, '01HP8X9K2MQRE4Y7V5N2M3F8O3', 'KN Ananthapadmanabhan', 'IND', 'TV_UMPIRE', '2024-01-01T00:00:00Z');

-- Mumbai Indians players
INSERT INTO player (id, public_id, full_name, known_as, date_of_birth, batting_style_id, bowling_style_id, nationality, created_at_utc) VALUES
-- Batsmen
(1, '01HP8X9K2MQRE4Y7V5N2M3F8P1', 'Rohit Gurunath Sharma', 'Rohit Sharma', '1987-04-30', 1, NULL, 'IND', '2024-01-01T00:00:00Z'),
(2, '01HP8X9K2MQRE4Y7V5N2M3F8P2', 'Ishan Kishan', 'Ishan Kishan', '1998-07-18', 2, NULL, 'IND', '2024-01-01T00:00:00Z'),
(3, '01HP8X9K2MQRE4Y7V5N2M3F8P3', 'Suryakumar Ashok Yadav', 'Suryakumar Yadav', '1990-09-14', 1, 7, 'IND', '2024-01-01T00:00:00Z'),
(4, '01HP8X9K2MQRE4Y7V5N2M3F8P4', 'Hardik Himanshu Pandya', 'Hardik Pandya', '1993-10-11', 1, 3, 'IND', '2024-01-01T00:00:00Z'),
(5, '01HP8X9K2MQRE4Y7V5N2M3F8P5', 'Kieron Adrian Pollard', 'Kieron Pollard', '1987-05-12', 1, 5, 'WI', '2024-01-01T00:00:00Z'),
-- Bowlers  
(6, '01HP8X9K2MQRE4Y7V5N2M3F8P6', 'Jasprit Jasbirsingh Bumrah', 'Jasprit Bumrah', '1993-12-06', 1, 1, 'IND', '2024-01-01T00:00:00Z'),
(7, '01HP8X9K2MQRE4Y7V5N2M3F8P7', 'Trent Alexander Boult', 'Trent Boult', '1989-07-22', 1, 2, 'NZ', '2024-01-01T00:00:00Z'),
(8, '01HP8X9K2MQRE4Y7V5N2M3F8P8', 'Rahul Chahar', 'Rahul Chahar', '1999-08-04', 1, 9, 'IND', '2024-01-01T00:00:00Z'),
(9, '01HP8X9K2MQRE4Y7V5N2M3F8P9', 'Krunal Himanshu Pandya', 'Krunal Pandya', '1991-03-24', 2, 11, 'IND', '2024-01-01T00:00:00Z'),
(10, '01HP8X9K2MQRE4Y7V5N2M3F8PA', 'Nathan Coulter-Nile', 'Nathan Coulter-Nile', '1987-10-11', 1, 1, 'AUS', '2024-01-01T00:00:00Z'),
(11, '01HP8X9K2MQRE4Y7V5N2M3F8PB', 'Quinton de Kock', 'Quinton de Kock', '1992-12-17', 2, NULL, 'SA', '2024-01-01T00:00:00Z');

-- Chennai Super Kings players  
INSERT INTO player (id, public_id, full_name, known_as, date_of_birth, batting_style_id, bowling_style_id, nationality, created_at_utc) VALUES
-- Batsmen
(12, '01HP8X9K2MQRE4Y7V5N2M3F8PC', 'Mahendra Singh Dhoni', 'MS Dhoni', '1981-07-07', 1, 5, 'IND', '2024-01-01T00:00:00Z'),
(13, '01HP8X9K2MQRE4Y7V5N2M3F8PD', 'Faf du Plessis', 'Faf du Plessis', '1984-07-13', 1, 5, 'SA', '2024-01-01T00:00:00Z'),
(14, '01HP8X9K2MQRE4Y7V5N2M3F8PE', 'Ruturaj Damodar Gaikwad', 'Ruturaj Gaikwad', '1997-01-31', 1, 7, 'IND', '2024-01-01T00:00:00Z'),
(15, '01HP8X9K2MQRE4Y7V5N2M3F8PF', 'Suresh Kumar Raina', 'Suresh Raina', '1986-11-27', 2, 7, 'IND', '2024-01-01T00:00:00Z'),
(16, '01HP8X9K2MQRE4Y7V5N2M3F8PG', 'Ambati Thirupathi Rayudu', 'Ambati Rayudu', '1985-09-23', 1, 7, 'IND', '2024-01-01T00:00:00Z'),
-- Bowlers
(17, '01HP8X9K2MQRE4Y7V5N2M3F8PH', 'Deepak Lokendrasingh Chahar', 'Deepak Chahar', '1992-08-07', 1, 3, 'IND', '2024-01-01T00:00:00Z'),
(18, '01HP8X9K2MQRE4Y7V5N2M3F8PI', 'Ravindra Anirudh Jadeja', 'Ravindra Jadeja', '1988-12-06', 2, 11, 'IND', '2024-01-01T00:00:00Z'),
(19, '01HP8X9K2MQRE4Y7V5N2M3F8PJ', 'Imran Tahir', 'Imran Tahir', '1979-03-27', 1, 9, 'SA', '2024-01-01T00:00:00Z'),
(20, '01HP8X9K2MQRE4Y7V5N2M3F8PK', 'Dwayne John Bravo', 'Dwayne Bravo', '1983-10-07', 1, 3, 'WI', '2024-01-01T00:00:00Z'),
(21, '01HP8X9K2MQRE4Y7V5N2M3F8PL', 'Shardul Narendra Thakur', 'Shardul Thakur', '1991-10-16', 1, 3, 'IND', '2024-01-01T00:00:00Z'),
(22, '01HP8X9K2MQRE4Y7V5N2M3F8PM', 'Sam Billings', 'Sam Billings', '1991-06-15', 1, NULL, 'ENG', '2024-01-01T00:00:00Z');

-- =============================================================================
-- VENUE AND TOURNAMENT
-- =============================================================================

INSERT INTO venue (id, public_id, name, city, country_code, timezone_name, capacity, ends_names, created_at_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8V1', 'Wankhede Stadium', 'Mumbai', 'IND', 'Asia/Kolkata', 33000, '["Pavilion End", "Tata End"]', '2024-01-01T00:00:00Z');

INSERT INTO tournament (id, public_id, name, season_label, match_type_id, start_date, end_date, points_system, created_at_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8T1', 'Indian Premier League', '2024', 6, '2024-03-22', '2024-05-26', '{"win":2,"loss":0,"tie":1,"no_result":1}', '2024-01-01T00:00:00Z');

INSERT INTO tournament_stage (id, public_id, tournament_id, name, stage_type_id, sort_order, start_date, end_date) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8S1', 1, 'League Stage', 2, 1, '2024-03-22', '2024-05-12');

INSERT INTO tournament_team (id, tournament_id, team_id, group_name) VALUES
(1, 1, 1, NULL),
(2, 1, 2, NULL);

-- =============================================================================
-- DEMO MATCH SETUP
-- =============================================================================

INSERT INTO match (id, public_id, tournament_id, stage_id, venue_id, match_type_id, status_id, 
                   start_time_utc, local_start_time, timezone_name, overs_limit, balls_per_over,
                   result_type, winner_team_id, notes, created_at_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8M1', 1, 1, 1, 6, 8, 
   '2024-04-15T14:30:00Z', '2024-04-15 20:00:00', 'Asia/Kolkata', 20, 6,
   'WIN', 1, 'Demo match for live scoring', '2024-04-15T12:00:00Z');

INSERT INTO match_team (id, match_id, team_id, is_home) VALUES
(1, 1, 1, TRUE),  -- Mumbai Indians (home)
(2, 1, 2, FALSE); -- Chennai Super Kings (away)

INSERT INTO match_official (id, match_id, official_id, role) VALUES
(1, 1, 1, 'FIELD_UMPIRE'),
(2, 1, 2, 'FIELD_UMPIRE'),
(3, 1, 3, 'TV_UMPIRE');

-- Toss: CSK wins and elects to bat first
INSERT INTO match_toss (match_id, won_by_team_id, decision_id, toss_time_utc) VALUES
(1, 2, 1, '2024-04-15T14:25:00Z'); -- CSK wins toss, bats first

-- =============================================================================
-- PLAYING XIs
-- =============================================================================

-- Mumbai Indians XI
INSERT INTO match_player (id, match_id, team_id, player_id, is_playing_xi, is_captain, is_wicketkeeper, batting_order) VALUES
(1, 1, 1, 1, TRUE, TRUE, FALSE, 1),   -- Rohit Sharma (c)
(2, 1, 1, 11, TRUE, FALSE, TRUE, 2),  -- Quinton de Kock (wk)
(3, 1, 1, 3, TRUE, FALSE, FALSE, 3),  -- Suryakumar Yadav
(4, 1, 1, 4, TRUE, FALSE, FALSE, 4),  -- Hardik Pandya
(5, 1, 1, 5, TRUE, FALSE, FALSE, 5),  -- Kieron Pollard
(6, 1, 1, 9, TRUE, FALSE, FALSE, 6),  -- Krunal Pandya
(7, 1, 1, 6, TRUE, FALSE, FALSE, 7),  -- Jasprit Bumrah
(8, 1, 1, 7, TRUE, FALSE, FALSE, 8),  -- Trent Boult
(9, 1, 1, 8, TRUE, FALSE, FALSE, 9),  -- Rahul Chahar
(10, 1, 1, 10, TRUE, FALSE, FALSE, 10), -- Nathan Coulter-Nile
(11, 1, 1, 2, TRUE, FALSE, FALSE, 11);  -- Ishan Kishan

-- Chennai Super Kings XI  
INSERT INTO match_player (id, match_id, team_id, player_id, is_playing_xi, is_captain, is_wicketkeeper, batting_order) VALUES
(12, 1, 2, 12, TRUE, TRUE, TRUE, 6),  -- MS Dhoni (c) (wk) 
(13, 1, 2, 13, TRUE, FALSE, FALSE, 1), -- Faf du Plessis
(14, 1, 2, 14, TRUE, FALSE, FALSE, 2), -- Ruturaj Gaikwad  
(15, 1, 2, 15, TRUE, FALSE, FALSE, 3), -- Suresh Raina
(16, 1, 2, 16, TRUE, FALSE, FALSE, 4), -- Ambati Rayudu
(17, 1, 2, 18, TRUE, FALSE, FALSE, 5), -- Ravindra Jadeja
(18, 1, 2, 20, TRUE, FALSE, FALSE, 7), -- Dwayne Bravo
(19, 1, 2, 17, TRUE, FALSE, FALSE, 8), -- Deepak Chahar
(20, 1, 2, 21, TRUE, FALSE, FALSE, 9), -- Shardul Thakur
(21, 1, 2, 19, TRUE, FALSE, FALSE, 10), -- Imran Tahir
(22, 1, 2, 22, TRUE, FALSE, FALSE, 11); -- Sam Billings

-- =============================================================================
-- INNINGS SETUP
-- =============================================================================

-- First Innings: CSK batting
INSERT INTO innings (id, public_id, match_id, seq_number, batting_team_id, bowling_team_id, 
                     is_completed, start_time_utc) VALUES
(1, '01HP8X9K2MQRE4Y7V5N2M3F8I1', 1, 1, 2, 1, FALSE, '2024-04-15T14:35:00Z');

-- Second Innings: MI chasing (target will be set after first innings)
INSERT INTO innings (id, public_id, match_id, seq_number, batting_team_id, bowling_team_id, 
                     is_completed, target_runs, start_time_utc) VALUES
(2, '01HP8X9K2MQRE4Y7V5N2M3F8I2', 1, 2, 1, 2, FALSE, 180, '2024-04-15T15:45:00Z'); -- Assuming 179 target

-- =============================================================================
-- POWERPLAY SETUP
-- =============================================================================

INSERT INTO powerplay (id, innings_id, powerplay_type, start_over, end_over, powerplay_number, max_fielders_outside_circle) VALUES
(1, 1, 'MANDATORY', 0, 5, 1, 2), -- First 6 overs powerplay (CSK innings)
(2, 2, 'MANDATORY', 0, 5, 1, 2); -- First 6 overs powerplay (MI innings)

-- =============================================================================
-- LIVE MATCH STATE
-- =============================================================================

INSERT INTO live_match_state (match_id, current_innings_id, current_over, current_ball, 
                             striker_id, non_striker_id, bowler_id, wicketkeeper_id,
                             is_powerplay, powerplay_type, powerplay_end_over, last_updated_utc) VALUES
(1, 1, 0, 1, 13, 14, 6, 11, TRUE, 'MANDATORY', 5, '2024-04-15T14:35:00Z');

-- =============================================================================
-- DEMO: 2 OVERS OF DELIVERIES (CSK batting first)
-- =============================================================================

-- OVER 1: Bumrah to Faf and Ruturaj
INSERT INTO delivery (id, public_id, innings_id, over_number, ball_in_over, is_legal_delivery, 
                     ts_utc, ball_sequence, striker_id, non_striker_id, bowler_id, wicketkeeper_id,
                     runs_batter, runs_extras, is_four, is_six, commentary_text) VALUES

-- Ball 1: Dot ball to Faf
(1, '01HP8X9K2MQRE4Y7V5N2M3F8D1', 1, 0, 1, TRUE, '2024-04-15T14:35:30Z', 1, 
 13, 14, 6, 11, 0, 0, FALSE, FALSE, 'Good length delivery outside off, Faf shoulders arms'),

-- Ball 2: Single to Faf 
(2, '01HP8X9K2MQRE4Y7V5N2M3F8D2', 1, 0, 2, TRUE, '2024-04-15T14:36:00Z', 2,
 13, 14, 6, 11, 1, 0, FALSE, FALSE, 'Faf works it to mid-wicket for a quick single'),

-- Ball 3: Dot to Ruturaj (on strike after single)
(3, '01HP8X9K2MQRE4Y7V5N2M3F8D3', 1, 0, 3, TRUE, '2024-04-15T14:36:30Z', 3,
 14, 13, 6, 11, 0, 0, FALSE, FALSE, 'Ruturaj defends solidly to cover'),

-- Ball 4: Wide down leg side  
(4, '01HP8X9K2MQRE4Y7V5N2M3F8D4', 1, 0, 4, FALSE, '2024-04-15T14:37:00Z', 4,
 14, 13, 6, 11, 0, 1, FALSE, FALSE, 'Wide down the leg side, Quinton de Kock collects'),

-- Ball 4 (again): Four through covers by Ruturaj
(5, '01HP8X9K2MQRE4Y7V5N2M3F8D5', 1, 0, 4, TRUE, '2024-04-15T14:37:30Z', 5,
 14, 13, 6, 11, 4, 0, TRUE, FALSE, 'Beautiful cover drive by Ruturaj! Races to the boundary'),

-- Ball 5: Two runs to Ruturaj
(6, '01HP8X9K2MQRE4Y7V5N2M3F8D6', 1, 0, 5, TRUE, '2024-04-15T14:38:00Z', 6,
 14, 13, 6, 11, 2, 0, FALSE, FALSE, 'Ruturaj clips it through mid-wicket for two'),

-- Ball 6: Dot ball to Ruturaj  
(7, '01HP8X9K2MQRE4Y7V5N2M3F8D7', 1, 0, 6, TRUE, '2024-04-15T14:38:30Z', 7,
 14, 13, 6, 11, 0, 0, FALSE, FALSE, 'Good yorker length, Ruturaj digs it out');

-- OVER 2: Boult to Ruturaj (retained strike)
INSERT INTO delivery (id, public_id, innings_id, over_number, ball_in_over, is_legal_delivery, 
                     ts_utc, ball_sequence, striker_id, non_striker_id, bowler_id, wicketkeeper_id,
                     runs_batter, runs_extras, extra_type_id, is_four, is_six, wicket_type_id,
                     out_player_id, fielder_id, commentary_text) VALUES

-- Ball 1: Six by Ruturaj!
(8, '01HP8X9K2MQRE4Y7V5N2M3F8D8', 1, 1, 1, TRUE, '2024-04-15T14:39:30Z', 8,
 14, 13, 7, 11, 6, 0, NULL, FALSE, TRUE, NULL, NULL, NULL, 
 'MAXIMUM! Ruturaj picks the length early and smashes it over mid-wicket!'),

-- Ball 2: No ball + Four! Free hit coming up
(9, '01HP8X9K2MQRE4Y7V5N2M3F8D9', 1, 1, 2, FALSE, '2024-04-15T14:40:00Z', 9,
 14, 13, 7, 11, 4, 1, 5, TRUE, FALSE, NULL, NULL, NULL,
 'NO BALL! And its edged through slip for FOUR! Free hit coming up'),

-- Ball 2 (Free hit): Two runs  
(10, '01HP8X9K2MQRE4Y7V5N2M3F8DA', 1, 1, 2, TRUE, '2024-04-15T14:40:30Z', 10,
 14, 13, 7, 11, 2, 0, NULL, FALSE, FALSE, NULL, NULL, NULL,
 'Free hit: Ruturaj swings across the line, gets two runs to deep square leg'),

-- Ball 3: WICKET! Ruturaj caught behind
(11, '01HP8X9K2MQRE4Y7V5N2M3F8DB', 1, 1, 3, TRUE, '2024-04-15T14:41:00Z', 11,
 14, 13, 7, 11, 0, 0, NULL, FALSE, FALSE, 4, 14, 11,
 'WICKET! Ruturaj edges it to the keeper! Boult strikes! Good catch by de Kock'),

-- Ball 4: Dot to new batsman Raina
(12, '01HP8X9K2MQRE4Y7V5N2M3F8DC', 1, 1, 4, TRUE, '2024-04-15T14:41:30Z', 12,
 15, 13, 7, 11, 0, 0, NULL, FALSE, FALSE, NULL, NULL, NULL,
 'Raina gets off the mark with a defensive push to cover'),

-- Ball 5: Single by Raina
(13, '01HP8X9K2MQRE4Y7V5N2M3F8DD', 1, 1, 5, TRUE, '2024-04-15T14:42:00Z', 13,
 15, 13, 7, 11, 1, 0, NULL, FALSE, FALSE, NULL, NULL, NULL,
 'Raina gets off the mark with a quick single to mid-on'),

-- Ball 6: Dot to Faf (back on strike)
(14, '01HP8X9K2MQRE4Y7V5N2M3F8DE', 1, 1, 6, TRUE, '2024-04-15T14:42:30Z', 14,
 13, 15, 7, 11, 0, 0, NULL, FALSE, FALSE, NULL, NULL, NULL,
 'Faf defends the last ball of the over safely back to the bowler');

-- =============================================================================
-- LIVE COMMENTARY
-- =============================================================================

INSERT INTO commentary (id, delivery_id, match_id, innings_id, commentary_text, commentary_type, 
                       timestamp_utc, sequence_number, commentator_name, is_key_moment) VALUES
(1, NULL, 1, NULL, 'Welcome to the Wankhede Stadium for this exciting IPL clash between Mumbai Indians and Chennai Super Kings!', 'GENERAL', '2024-04-15T14:30:00Z', 1, 'Harsha Bhogle', FALSE),
(2, NULL, 1, NULL, 'CSK have won the toss and elected to bat first. The pitch looks good for batting.', 'GENERAL', '2024-04-15T14:25:00Z', 2, 'Harsha Bhogle', TRUE),
(3, 5, 1, 1, 'What a shot! Ruturaj announces his arrival with a glorious cover drive for four', 'BOUNDARY', '2024-04-15T14:37:30Z', 3, 'Sunil Gavaskar', TRUE),
(4, 8, 1, 1, 'MASSIVE HIT! Ruturaj is not holding back, thats sailed over the mid-wicket boundary', 'BOUNDARY', '2024-04-15T14:39:30Z', 4, 'Shane Warne', TRUE),
(5, 11, 1, 1, 'Boult gets his revenge! What a delivery, Ruturaj has to go after a brilliant start', 'WICKET', '2024-04-15T14:41:00Z', 5, 'Ian Bishop', TRUE);

-- =============================================================================
-- MILESTONE TRACKING
-- =============================================================================

INSERT INTO milestone (id, delivery_id, match_id, player_id, milestone_type, milestone_value, 
                      balls_taken, milestone_ball_id, achieved_at_utc) VALUES
(1, 8, 1, 14, 'FIRST_SIX', 6, 4, 8, '2024-04-15T14:39:30Z'); -- Ruturaj's six

-- =============================================================================
-- BOWLING SPELL TRACKING
-- =============================================================================

INSERT INTO bowling_spell (id, innings_id, bowler_id, start_over, end_over, spell_number, is_opening_spell) VALUES
(1, 1, 6, 0, 0, 1, TRUE),  -- Bumrah's first over
(2, 1, 7, 1, 1, 1, FALSE); -- Boult's first over

-- Update with current stats
UPDATE bowling_spell SET 
  overs_bowled = 1.0,
  runs_conceded = 8,
  wickets_taken = 0,
  maidens = 0
WHERE id = 1;

UPDATE bowling_spell SET 
  overs_bowled = 1.0, 
  runs_conceded = 14,
  wickets_taken = 1,
  maidens = 0
WHERE id = 2;
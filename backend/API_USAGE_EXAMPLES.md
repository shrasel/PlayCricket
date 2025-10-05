# PlayCricket API - Usage Examples

## Quick Start Guide

### 1. Create Teams
```bash
# Create Team 1
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "India",
    "short_name": "IND",
    "country_code": "IN",
    "logo_url": "https://example.com/india-logo.png"
  }'

# Create Team 2
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Australia",
    "short_name": "AUS",
    "country_code": "AU",
    "logo_url": "https://example.com/aus-logo.png"
  }'
```

### 2. Create Players
```bash
# Create Batsman
curl -X POST http://localhost:8000/api/v1/players \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Virat Kohli",
    "known_as": "Virat",
    "dob": "1988-11-05",
    "batting_style": "Right-hand bat",
    "bowling_style": "Right-arm medium"
  }'

# Create Bowler
curl -X POST http://localhost:8000/api/v1/players \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jasprit Bumrah",
    "known_as": "Boom Boom",
    "dob": "1993-12-06",
    "batting_style": "Right-hand bat",
    "bowling_style": "Right-arm fast"
  }'
```

### 3. Create Venue
```bash
curl -X POST http://localhost:8000/api/v1/venues \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eden Gardens",
    "city": "Kolkata",
    "country_code": "IN",
    "timezone_name": "Asia/Kolkata",
    "ends_names": "Pavilion End, High Court End"
  }'
```

### 4. Create Tournament
```bash
curl -X POST http://localhost:8000/api/v1/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ICC T20 World Cup",
    "short_name": "T20 WC",
    "season": "2024",
    "match_type": "T20",
    "start_date": "2024-06-01",
    "end_date": "2024-06-29",
    "points_system": {
      "win": 2,
      "loss": 0,
      "tie": 1,
      "no_result": 1
    }
  }'
```

### 5. Create Match
```bash
curl -X POST http://localhost:8000/api/v1/matches \
  -H "Content-Type: application/json" \
  -d '{
    "venue_id": "{venue_ulid}",
    "tournament_id": "{tournament_ulid}",
    "match_type": "T20",
    "status": "SCHEDULED",
    "scheduled_start": "2024-06-15T14:30:00Z",
    "overs_per_innings": 20,
    "teams": [
      {
        "team_id": "{india_team_ulid}",
        "is_home": true
      },
      {
        "team_id": "{australia_team_ulid}",
        "is_home": false
      }
    ]
  }'
```

### 6. Set Match Toss
```bash
curl -X POST "http://localhost:8000/api/v1/matches/{match_id}/toss" \
  -H "Content-Type: application/json" \
  -d '{
    "toss_winner_id": "{india_team_ulid}",
    "elected_to": "BAT"
  }'
```

### 7. Start Match (Update Status)
```bash
curl -X PATCH "http://localhost:8000/api/v1/matches/{match_id}/status?new_status=LIVE" \
  -H "Content-Type: application/json"
```

### 8. Create Innings
```bash
curl -X POST http://localhost:8000/api/v1/innings \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "{match_ulid}",
    "seq_number": 1,
    "batting_team_id": "{india_team_ulid}",
    "bowling_team_id": "{australia_team_ulid}",
    "target_runs": null
  }'
```

### 9. Record Ball-by-Ball Deliveries

#### Normal Delivery (Dot Ball)
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 1,
    "ball_in_over": 1,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 0,
    "runs_extras": 0,
    "commentary_text": "Good length delivery, defended back to the bowler"
  }'
```

#### Boundary (Four)
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 1,
    "ball_in_over": 2,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 4,
    "runs_extras": 0,
    "is_four": true,
    "wagon_x": 45.0,
    "wagon_y": 30.0,
    "pitch_x": 12.0,
    "pitch_y": 3.5,
    "commentary_text": "Lovely cover drive! Races away to the boundary"
  }'
```

#### Six
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 2,
    "ball_in_over": 3,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 6,
    "runs_extras": 0,
    "is_six": true,
    "wagon_x": 0.0,
    "wagon_y": 60.0,
    "pitch_x": 10.0,
    "pitch_y": 4.0,
    "commentary_text": "That is HUGE! Straight down the ground for a maximum!"
  }'
```

#### Wide
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 3,
    "ball_in_over": 1,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 0,
    "runs_extras": 1,
    "extra_type": "WIDE",
    "commentary_text": "Wide down the leg side, umpire signals wide"
  }'
```

#### No Ball
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 3,
    "ball_in_over": 2,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 1,
    "runs_extras": 1,
    "extra_type": "NO_BALL",
    "commentary_text": "No ball! Overstepped, free hit coming up"
  }'
```

#### Wicket (Bowled)
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 5,
    "ball_in_over": 4,
    "striker_id": "{virat_kohli_ulid}",
    "non_striker_id": "{rohit_sharma_ulid}",
    "bowler_id": "{pat_cummins_ulid}",
    "runs_batter": 0,
    "runs_extras": 0,
    "wicket_type": "BOWLED",
    "out_player_id": "{virat_kohli_ulid}",
    "commentary_text": "BOWLED! What a delivery! Virat Kohli departs for 45"
  }'
```

#### Wicket (Caught)
```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/ball-by-ball?innings_id={innings_ulid}" \
  -H "Content-Type: application/json" \
  -d '{
    "over_number": 8,
    "ball_in_over": 2,
    "striker_id": "{rohit_sharma_ulid}",
    "non_striker_id": "{kl_rahul_ulid}",
    "bowler_id": "{mitchell_starc_ulid}",
    "runs_batter": 0,
    "runs_extras": 0,
    "wicket_type": "CAUGHT",
    "out_player_id": "{rohit_sharma_ulid}",
    "fielder_id": "{david_warner_ulid}",
    "commentary_text": "CAUGHT! Warner takes a brilliant catch at cover"
  }'
```

### 10. Get Live Score
```bash
curl http://localhost:8000/api/v1/innings/{innings_id}/score
```

Response:
```json
{
  "total_runs": 125,
  "total_wickets": 3,
  "total_overs": 15.2,
  "is_all_out": false,
  "run_rate": 8.17
}
```

### 11. Get Current Partnership
```bash
curl http://localhost:8000/api/v1/innings/{innings_id}/partnership
```

Response:
```json
{
  "striker_id": "{player_ulid}",
  "non_striker_id": "{player_ulid}",
  "partnership_runs": 45,
  "partnership_balls": 28
}
```

### 12. Get Batsman Stats
```bash
curl "http://localhost:8000/api/v1/deliveries/innings/{innings_id}/batsman/{player_id}/stats"
```

Response:
```json
{
  "runs": 73,
  "balls_faced": 49,
  "fours": 8,
  "sixes": 2,
  "strike_rate": 148.98,
  "is_out": true,
  "is_not_out": false
}
```

### 13. Get Bowler Stats
```bash
curl "http://localhost:8000/api/v1/deliveries/innings/{innings_id}/bowler/{player_id}/stats"
```

Response:
```json
{
  "overs": 4.0,
  "runs_conceded": 23,
  "wickets": 3,
  "economy_rate": 5.75,
  "wides": 2,
  "no_balls": 1,
  "fours_conceded": 2,
  "sixes_conceded": 0
}
```

### 14. Get Over Summary
```bash
curl "http://localhost:8000/api/v1/deliveries/innings/{innings_id}/over/5"
```

Response:
```json
{
  "over_number": 5,
  "total_runs": 12,
  "wickets": 1,
  "legal_balls": 6,
  "extras": 1,
  "deliveries": [...]
}
```

### 15. Get Wagon Wheel Data
```bash
curl "http://localhost:8000/api/v1/deliveries/innings/{innings_id}/wagon-wheel?player_id={player_id}"
```

Response:
```json
[
  {
    "x": 45.0,
    "y": 30.0,
    "runs": 4,
    "is_four": true,
    "is_six": false
  },
  {
    "x": 0.0,
    "y": 60.0,
    "runs": 6,
    "is_four": false,
    "is_six": true
  }
]
```

### 16. Get Pitch Map Data
```bash
curl "http://localhost:8000/api/v1/deliveries/innings/{innings_id}/pitch-map?bowler_id={bowler_id}"
```

Response:
```json
[
  {
    "x": 12.0,
    "y": 3.5,
    "runs_conceded": 4,
    "wicket": false,
    "wicket_type": null
  },
  {
    "x": 10.0,
    "y": 4.0,
    "runs_conceded": 0,
    "wicket": true,
    "wicket_type": "BOWLED"
  }
]
```

### 17. Get Full Scorecard
```bash
curl http://localhost:8000/api/v1/stats/matches/{match_id}/scorecard
```

Response:
```json
{
  "match_id": "...",
  "match_type": "T20",
  "status": "COMPLETED",
  "venue": {
    "id": "...",
    "name": "Eden Gardens",
    "city": "Kolkata"
  },
  "innings": [
    {
      "innings_number": 1,
      "batting_team_name": "India",
      "total_runs": 185,
      "total_wickets": 6,
      "total_overs": 20.0,
      "run_rate": 9.25,
      "batting": [
        {
          "player_name": "Virat Kohli",
          "runs": 73,
          "balls_faced": 49,
          "fours": 8,
          "sixes": 2,
          "strike_rate": 148.98,
          "is_out": true,
          "wicket_type": "CAUGHT"
        }
      ],
      "bowling": [
        {
          "player_name": "Pat Cummins",
          "overs": 4.0,
          "runs_conceded": 35,
          "wickets": 2,
          "economy_rate": 8.75,
          "wides": 2,
          "no_balls": 0
        }
      ]
    }
  ],
  "result": {
    "winning_team_name": "India",
    "result_type": "NORMAL",
    "result_margin": "India won by 7 wickets"
  }
}
```

### 18. Get Player Career Stats
```bash
curl http://localhost:8000/api/v1/stats/players/{player_id}/career
```

Response:
```json
{
  "player": {
    "full_name": "Virat Kohli",
    "batting_style": "Right-hand bat",
    "bowling_style": "Right-arm medium"
  },
  "batting": {
    "innings": 254,
    "runs": 12169,
    "balls_faced": 11428,
    "average": 59.07,
    "strike_rate": 106.48,
    "fours": 1202,
    "sixes": 108,
    "dismissals": 206,
    "not_outs": 48
  },
  "bowling": {
    "innings": 23,
    "overs": 32.4,
    "runs_conceded": 246,
    "wickets": 4,
    "average": 61.50,
    "economy_rate": 7.53
  }
}
```

### 19. Close Innings
```bash
curl -X POST "http://localhost:8000/api/v1/innings/{innings_id}/close?reason=NORMAL"
```

### 20. Complete Match
```bash
curl -X PATCH "http://localhost:8000/api/v1/matches/{match_id}/status?new_status=COMPLETED"
```

## Search & Filter Examples

### Search Teams
```bash
curl "http://localhost:8000/api/v1/teams?search=india&limit=10"
```

### Filter Players by Age
```bash
curl "http://localhost:8000/api/v1/players?min_age=25&max_age=35"
```

### Get Live Matches
```bash
curl http://localhost:8000/api/v1/matches/live
```

### Filter Matches by Tournament
```bash
curl "http://localhost:8000/api/v1/matches?tournament_id={tournament_ulid}"
```

### Get Active Tournaments
```bash
curl "http://localhost:8000/api/v1/tournaments?status=active"
```

## Pagination Example
```bash
# Get first 20 items
curl "http://localhost:8000/api/v1/teams?skip=0&limit=20"

# Get next 20 items
curl "http://localhost:8000/api/v1/teams?skip=20&limit=20"
```

## Error Handling

### 404 Not Found
```json
{
  "detail": "Player with ID 'xyz' not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Exactly 2 teams are required for a match"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Tips

1. **Always use public ULIDs** in API calls, not internal database IDs
2. **Set match status to LIVE** before recording deliveries
3. **Create innings** before recording deliveries
4. **Use ball-by-ball endpoint** for live scoring - it validates everything
5. **Get wagon wheel data** for shot visualization
6. **Get pitch map data** for bowling analysis
7. **Use scorecard endpoint** for complete match summary
8. **Filter by status** to get LIVE, SCHEDULED, or COMPLETED matches

## Rate Limits

Currently no rate limits, but recommended for production:
- 100 requests/minute per IP for read endpoints
- 20 requests/minute per IP for write endpoints
- 5 requests/minute for ball-by-ball scoring

## Next Steps

1. Add authentication (JWT tokens)
2. Implement WebSocket for real-time updates
3. Add push notifications for match events
4. Integrate commentary AI
5. Add video highlight URLs
6. Implement fantasy cricket scoring

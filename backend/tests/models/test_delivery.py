"""Tests for Delivery model - ball-by-ball tracking."""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Match, Team, Player, Innings, Delivery, Venue


class TestDeliveryModel:
    """Test cases for Delivery model."""

    @pytest.mark.asyncio
    async def test_create_delivery_with_required_fields(self, test_db):
        """Test creating a delivery with required fields."""
        # Create dependencies
        venue = Venue(name="Delivery Ground", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A", short_name="TA")
        team2 = Team(name="Team B", short_name="TB")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player")
        non_striker = Player(full_name="Non-Striker Player")
        bowler = Player(full_name="Bowler Player")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        # Create delivery
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id
        )
        test_db.add(delivery)
        await test_db.commit()
        
        # Verify
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.public_id is not None
        assert len(saved.public_id) == 26
        assert saved.innings_id == innings.id
        assert saved.over_number == 1
        assert saved.ball_in_over == 1
        assert saved.is_legal_delivery is True
        assert saved.runs_batter == 0
        assert saved.runs_extras == 0
        assert saved.is_four is False
        assert saved.is_six is False

    @pytest.mark.asyncio
    async def test_create_delivery_with_runs(self, test_db):
        """Test creating a delivery with runs scored."""
        venue = Venue(name="Delivery Ground 2", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A2", short_name="TA2")
        team2 = Team(name="Team B2", short_name="TB2")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 2")
        non_striker = Player(full_name="Non-Striker Player 2")
        bowler = Player(full_name="Bowler Player 2")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="ODI",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        # Create delivery with boundary
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=3,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=4,
            is_four=True
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.runs_batter == 4
        assert saved.is_four is True
        assert saved.is_six is False

    @pytest.mark.asyncio
    async def test_create_delivery_six(self, test_db):
        """Test creating a delivery with a six."""
        venue = Venue(name="Delivery Ground 3", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A3", short_name="TA3")
        team2 = Team(name="Team B3", short_name="TB3")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 3")
        non_striker = Player(full_name="Non-Striker Player 3")
        bowler = Player(full_name="Bowler Player 3")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        delivery = Delivery(
            innings_id=innings.id,
            over_number=5,
            ball_in_over=4,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=6,
            is_six=True
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.runs_batter == 6
        assert saved.is_six is True

    @pytest.mark.asyncio
    async def test_create_delivery_with_extra(self, test_db):
        """Test creating a delivery with extras."""
        venue = Venue(name="Delivery Ground 4", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A4", short_name="TA4")
        team2 = Team(name="Team B4", short_name="TB4")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 4")
        non_striker = Player(full_name="Non-Striker Player 4")
        bowler = Player(full_name="Bowler Player 4")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        # Wide delivery
        delivery = Delivery(
            innings_id=innings.id,
            over_number=2,
            ball_in_over=1,
            is_legal_delivery=False,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_extras=1,
            extra_type="WIDE"
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.is_legal_delivery is False
        assert saved.runs_extras == 1
        assert saved.extra_type == "WIDE"

    @pytest.mark.asyncio
    async def test_create_delivery_with_wicket(self, test_db):
        """Test creating a delivery with a wicket."""
        venue = Venue(name="Delivery Ground 5", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A5", short_name="TA5")
        team2 = Team(name="Team B5", short_name="TB5")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 5")
        non_striker = Player(full_name="Non-Striker Player 5")
        bowler = Player(full_name="Bowler Player 5")
        fielder = Player(full_name="Fielder Player 5")
        test_db.add_all([striker, non_striker, bowler, fielder])
        
        match = Match(
            venue_id=venue.id,
            match_type="ODI",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        # Caught delivery
        delivery = Delivery(
            innings_id=innings.id,
            over_number=10,
            ball_in_over=3,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            wicket_type="CAUGHT",
            out_player_id=striker.id,
            fielder_id=fielder.id
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.wicket_type == "CAUGHT"
        assert saved.out_player_id == striker.id
        assert saved.fielder_id == fielder.id

    @pytest.mark.asyncio
    async def test_delivery_with_coordinates(self, test_db):
        """Test creating a delivery with wagon and pitch coordinates."""
        venue = Venue(name="Delivery Ground 6", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A6", short_name="TA6")
        team2 = Team(name="Team B6", short_name="TB6")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 6")
        non_striker = Player(full_name="Non-Striker Player 6")
        bowler = Player(full_name="Bowler Player 6")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=4,
            is_four=True,
            wagon_x=75.5,
            wagon_y=50.0,
            pitch_x=30.0,
            pitch_y=45.0
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.wagon_x == 75.5
        assert saved.wagon_y == 50.0
        assert saved.pitch_x == 30.0
        assert saved.pitch_y == 45.0

    @pytest.mark.asyncio
    async def test_delivery_with_commentary(self, test_db):
        """Test creating a delivery with commentary."""
        venue = Venue(name="Delivery Ground 7", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A7", short_name="TA7")
        team2 = Team(name="Team B7", short_name="TB7")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 7")
        non_striker = Player(full_name="Non-Striker Player 7")
        bowler = Player(full_name="Bowler Player 7")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=6,
            is_six=True,
            commentary_text="What a shot! Massive six over mid-wicket!"
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.commentary_text == "What a shot! Massive six over mid-wicket!"

    @pytest.mark.asyncio
    async def test_delivery_replaces_another(self, test_db):
        """Test creating a delivery that replaces another (correction)."""
        venue = Venue(name="Delivery Ground 8", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A8", short_name="TA8")
        team2 = Team(name="Team B8", short_name="TB8")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 8")
        non_striker = Player(full_name="Non-Striker Player 8")
        bowler = Player(full_name="Bowler Player 8")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        # Original delivery
        original = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=1
        )
        test_db.add(original)
        await test_db.flush()
        
        # Corrected delivery
        corrected = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id,
            runs_batter=2,
            replaces_delivery_id=original.id
        )
        test_db.add(corrected)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        all_deliveries = result.scalars().all()
        assert len(all_deliveries) == 2
        corrected_delivery = [d for d in all_deliveries if d.replaces_delivery_id is not None][0]
        assert corrected_delivery.replaces_delivery_id == original.id

    @pytest.mark.asyncio
    async def test_delivery_relationships(self, test_db):
        """Test relationships between Delivery and related models."""
        venue = Venue(name="Delivery Ground 9", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A9", short_name="TA9")
        team2 = Team(name="Team B9", short_name="TB9")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 9")
        non_striker = Player(full_name="Non-Striker Player 9")
        bowler = Player(full_name="Bowler Player 9")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.innings.id == innings.id
        assert saved.striker.id == striker.id
        assert saved.non_striker.id == non_striker.id
        assert saved.bowler.id == bowler.id

    @pytest.mark.asyncio
    async def test_delivery_timestamps(self, test_db):
        """Test that delivery timestamps are automatically set."""
        venue = Venue(name="Delivery Ground 10", city="Test City")
        test_db.add(venue)
        
        team1 = Team(name="Team A10", short_name="TA10")
        team2 = Team(name="Team B10", short_name="TB10")
        test_db.add_all([team1, team2])
        
        striker = Player(full_name="Striker Player 10")
        non_striker = Player(full_name="Non-Striker Player 10")
        bowler = Player(full_name="Bowler Player 10")
        test_db.add_all([striker, non_striker, bowler])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=team1.id,
            bowling_team_id=team2.id
        )
        test_db.add(innings)
        await test_db.flush()
        
        delivery = Delivery(
            innings_id=innings.id,
            over_number=1,
            ball_in_over=1,
            is_legal_delivery=True,
            ts_utc=datetime.now(timezone.utc).isoformat(),
            striker_id=striker.id,
            non_striker_id=non_striker.id,
            bowler_id=bowler.id
        )
        test_db.add(delivery)
        await test_db.commit()
        
        result = await test_db.execute(select(Delivery))
        saved = result.scalar_one()
        assert saved.created_at is not None
        assert saved.updated_at is not None
        assert saved.created_at.tzinfo is not None

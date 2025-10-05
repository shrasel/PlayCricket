"""Tests for Innings model."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Match, Team, Innings, Venue


class TestInningsModel:
    """Test cases for Innings model."""

    @pytest.mark.asyncio
    async def test_create_innings_with_required_fields(self, test_db):
        """Test creating an innings with required fields."""
        # Create dependencies
        venue = Venue(name="Innings Ground", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team", short_name="BAT")
        bowling_team = Team(name="Bowling Team", short_name="BWL")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        # Create innings
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id
        )
        test_db.add(innings)
        await test_db.commit()
        
        # Verify
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.public_id is not None
        assert len(saved.public_id) == 26
        assert saved.match_id == match.id
        assert saved.seq_number == 1
        assert saved.batting_team_id == batting_team.id
        assert saved.bowling_team_id == bowling_team.id
        assert saved.follow_on is False
        assert saved.declared is False
        assert saved.forfeited is False
        assert saved.target_runs is None

    @pytest.mark.asyncio
    async def test_create_innings_with_all_fields(self, test_db):
        """Test creating an innings with all optional fields."""
        venue = Venue(name="Innings Ground 2", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 2", short_name="BAT2")
        bowling_team = Team(name="Bowling Team 2", short_name="BWL2")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="TEST",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        # Create innings with all fields (follow-on scenario)
        innings = Innings(
            match_id=match.id,
            seq_number=3,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id,
            follow_on=True,
            declared=False,
            forfeited=False,
            target_runs=350
        )
        test_db.add(innings)
        await test_db.commit()
        
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.follow_on is True
        assert saved.declared is False
        assert saved.forfeited is False
        assert saved.target_runs == 350

    @pytest.mark.asyncio
    async def test_innings_public_id_is_unique(self, test_db):
        """Test that public_id is unique across innings."""
        venue = Venue(name="Innings Ground 3", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 3", short_name="BAT3")
        bowling_team = Team(name="Bowling Team 3", short_name="BWL3")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="ODI",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings1 = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id
        )
        innings2 = Innings(
            match_id=match.id,
            seq_number=2,
            batting_team_id=bowling_team.id,
            bowling_team_id=batting_team.id
        )
        test_db.add_all([innings1, innings2])
        await test_db.commit()
        
        # Verify both have unique public_ids
        result = await test_db.execute(select(Innings))
        all_innings = result.scalars().all()
        assert len(all_innings) == 2
        assert all_innings[0].public_id != all_innings[1].public_id

    @pytest.mark.asyncio
    async def test_innings_unique_constraint(self, test_db):
        """Test that seq_number must be unique per match."""
        venue = Venue(name="Innings Ground 4", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 4", short_name="BAT4")
        bowling_team = Team(name="Bowling Team 4", short_name="BWL4")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings1 = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id
        )
        test_db.add(innings1)
        await test_db.commit()
        
        # Try to create another innings with same seq_number
        innings2 = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=bowling_team.id,
            bowling_team_id=batting_team.id
        )
        test_db.add(innings2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_innings_declared(self, test_db):
        """Test creating a declared innings."""
        venue = Venue(name="Innings Ground 5", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 5", short_name="BAT5")
        bowling_team = Team(name="Bowling Team 5", short_name="BWL5")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="TEST",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=1,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id,
            declared=True
        )
        test_db.add(innings)
        await test_db.commit()
        
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.declared is True

    @pytest.mark.asyncio
    async def test_innings_forfeited(self, test_db):
        """Test creating a forfeited innings."""
        venue = Venue(name="Innings Ground 6", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 6", short_name="BAT6")
        bowling_team = Team(name="Bowling Team 6", short_name="BWL6")
        test_db.add_all([batting_team, bowling_team])
        
        match = Match(
            venue_id=venue.id,
            match_type="TEST",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        innings = Innings(
            match_id=match.id,
            seq_number=2,
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id,
            forfeited=True
        )
        test_db.add(innings)
        await test_db.commit()
        
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.forfeited is True

    @pytest.mark.asyncio
    async def test_innings_relationships(self, test_db):
        """Test relationships between Innings and related models."""
        venue = Venue(name="Innings Ground 7", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 7", short_name="BAT7")
        bowling_team = Team(name="Bowling Team 7", short_name="BWL7")
        test_db.add_all([batting_team, bowling_team])
        
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
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id,
            target_runs=250
        )
        test_db.add(innings)
        await test_db.commit()
        
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.match.id == match.id
        assert saved.batting_team.id == batting_team.id
        assert saved.bowling_team.id == bowling_team.id

    @pytest.mark.asyncio
    async def test_innings_timestamps(self, test_db):
        """Test that timestamps are automatically set."""
        venue = Venue(name="Innings Ground 8", city="Test City")
        test_db.add(venue)
        
        batting_team = Team(name="Batting Team 8", short_name="BAT8")
        bowling_team = Team(name="Bowling Team 8", short_name="BWL8")
        test_db.add_all([batting_team, bowling_team])
        
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
            batting_team_id=batting_team.id,
            bowling_team_id=bowling_team.id
        )
        test_db.add(innings)
        await test_db.commit()
        
        result = await test_db.execute(select(Innings))
        saved = result.scalar_one()
        assert saved.created_at is not None
        assert saved.updated_at is not None
        assert saved.created_at.tzinfo is not None
        assert saved.updated_at.tzinfo is not None

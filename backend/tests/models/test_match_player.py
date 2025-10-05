"""Tests for MatchPlayer model."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Match, Team, Player, MatchPlayer, Venue


class TestMatchPlayerModel:
    """Test cases for MatchPlayer model."""

    @pytest.mark.asyncio
    async def test_create_match_player_with_required_fields(self, test_db):
        """Test creating a match player with required fields."""
        # Create dependencies
        venue = Venue(name="Test Ground", city="Test City")
        test_db.add(venue)
        
        team = Team(name="Test Team", short_name="TT")
        test_db.add(team)
        
        player = Player(full_name="Test Player")
        test_db.add(player)
        
        await test_db.flush()
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="LIVE",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        # Create match player
        match_player = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id
        )
        test_db.add(match_player)
        await test_db.commit()
        
        # Verify
        result = await test_db.execute(select(MatchPlayer))
        saved = result.scalar_one()
        assert saved.match_id == match.id
        assert saved.team_id == team.id
        assert saved.player_id == player.id
        assert saved.is_playing_xi is True  # Default
        assert saved.is_captain is False  # Default
        assert saved.is_wicketkeeper is False  # Default
        assert saved.batting_order is None

    @pytest.mark.asyncio
    async def test_create_match_player_with_all_fields(self, test_db):
        """Test creating a match player with all optional fields."""
        # Create dependencies
        venue = Venue(name="Test Ground 2", city="Test City")
        test_db.add(venue)
        
        team = Team(name="Test Team 2", short_name="TT2")
        test_db.add(team)
        
        player = Player(full_name="Captain Player")
        test_db.add(player)
        
        match = Match(
            venue_id=None,
            match_type="ODI",
            status="SCHEDULED",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        # Create match player with all fields
        match_player = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id,
            is_playing_xi=True,
            is_captain=True,
            is_wicketkeeper=True,
            batting_order=1
        )
        test_db.add(match_player)
        await test_db.commit()
        
        # Verify
        result = await test_db.execute(select(MatchPlayer))
        saved = result.scalar_one()
        assert saved.is_playing_xi is True
        assert saved.is_captain is True
        assert saved.is_wicketkeeper is True
        assert saved.batting_order == 1

    @pytest.mark.asyncio
    async def test_match_player_unique_constraint(self, test_db):
        """Test that the same player can't be added twice to the same match."""
        venue = Venue(name="Test Ground 3", city="Test City")
        test_db.add(venue)
        
        team = Team(name="Test Team 3", short_name="TT3")
        test_db.add(team)
        
        player = Player(full_name="Duplicate Player")
        test_db.add(player)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        # Add player first time
        mp1 = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id
        )
        test_db.add(mp1)
        await test_db.commit()
        
        # Try to add same player again
        mp2 = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id
        )
        test_db.add(mp2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()

    @pytest.mark.asyncio
    async def test_match_player_relationships(self, test_db):
        """Test relationships between MatchPlayer and related models."""
        venue = Venue(name="Test Ground 4", city="Test City")
        test_db.add(venue)
        
        team = Team(name="Test Team 4", short_name="TT4")
        test_db.add(team)
        
        player = Player(full_name="Related Player")
        test_db.add(player)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        match_player = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id,
            is_captain=True
        )
        test_db.add(match_player)
        await test_db.commit()
        
        # Verify relationships
        result = await test_db.execute(select(MatchPlayer))
        saved = result.scalar_one()
        assert saved.match.id == match.id
        assert saved.team.id == team.id
        assert saved.player.id == player.id

    @pytest.mark.asyncio
    async def test_substitute_player(self, test_db):
        """Test creating a substitute player (not in playing XI)."""
        venue = Venue(name="Test Ground 5", city="Test City")
        test_db.add(venue)
        
        team = Team(name="Test Team 5", short_name="TT5")
        test_db.add(team)
        
        player = Player(full_name="Substitute Player")
        test_db.add(player)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6
        )
        test_db.add(match)
        await test_db.flush()
        
        # Create substitute (not in playing XI)
        match_player = MatchPlayer(
            match_id=match.id,
            team_id=team.id,
            player_id=player.id,
            is_playing_xi=False
        )
        test_db.add(match_player)
        await test_db.commit()
        
        result = await test_db.execute(select(MatchPlayer))
        saved = result.scalar_one()
        assert saved.is_playing_xi is False
        assert saved.batting_order is None

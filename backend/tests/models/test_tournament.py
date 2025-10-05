"""Tests for Tournament model."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
@pytest.mark.unit
class TestTournamentModel:
    """Test Tournament model basic functionality"""
    
    async def test_create_tournament_with_required_fields(self, test_db: AsyncSession):
        """Test creating a tournament with only required fields"""
        from app.models.tournament import Tournament
        
        tournament = Tournament(
            name="Indian Premier League",
            match_type="T20",
        )
        
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.id is not None
        assert tournament.public_id is not None  # Should auto-generate ULID
        assert tournament.name == "Indian Premier League"
        assert tournament.match_type == "T20"
        assert tournament.created_at is not None
        
    async def test_create_tournament_with_all_fields(self, test_db: AsyncSession):
        """Test creating a tournament with all optional fields"""
        from app.models.tournament import Tournament
        
        tournament = Tournament(
            name="ICC Cricket World Cup",
            season_label="2023",
            match_type="ODI",
            points_system={"win": 2, "loss": 0, "tie": 1, "no_result": 1},
        )
        
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.name == "ICC Cricket World Cup"
        assert tournament.season_label == "2023"
        assert tournament.match_type == "ODI"
        assert tournament.points_system == {"win": 2, "loss": 0, "tie": 1, "no_result": 1}
        
    async def test_tournament_public_id_is_unique(self, test_db: AsyncSession):
        """Test that public_id is unique across tournaments"""
        from app.models.tournament import Tournament
        
        tournament1 = Tournament(name="Tournament One", match_type="T20")
        tournament2 = Tournament(name="Tournament Two", match_type="ODI")
        
        test_db.add_all([tournament1, tournament2])
        await test_db.commit()
        
        assert tournament1.public_id != tournament2.public_id
        
    async def test_tournament_name_season_must_be_unique(self, test_db: AsyncSession):
        """Test that combination of name and season_label must be unique"""
        from app.models.tournament import Tournament
        
        tournament1 = Tournament(
            name="IPL",
            season_label="2024",
            match_type="T20",
        )
        test_db.add(tournament1)
        await test_db.commit()
        
        # Try to create another tournament with same name and season
        tournament2 = Tournament(
            name="IPL",
            season_label="2024",
            match_type="T20",
        )
        test_db.add(tournament2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()
            
    async def test_tournament_same_name_different_season(self, test_db: AsyncSession):
        """Test that same tournament name can exist with different seasons"""
        from app.models.tournament import Tournament
        
        tournament1 = Tournament(name="IPL", season_label="2023", match_type="T20")
        tournament2 = Tournament(name="IPL", season_label="2024", match_type="T20")
        
        test_db.add_all([tournament1, tournament2])
        await test_db.commit()
        await test_db.refresh(tournament1)
        await test_db.refresh(tournament2)
        
        assert tournament1.id != tournament2.id
        assert tournament1.season_label == "2023"
        assert tournament2.season_label == "2024"
        
    async def test_get_tournament_by_public_id(self, test_db: AsyncSession):
        """Test retrieving tournament by public_id"""
        from app.models.tournament import Tournament
        
        tournament = Tournament(
            name="Big Bash League",
            season_label="2024-25",
            match_type="T20",
        )
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        # Query by public_id
        result = await test_db.execute(
            select(Tournament).where(Tournament.public_id == tournament.public_id)
        )
        found_tournament = result.scalar_one()
        
        assert found_tournament.id == tournament.id
        assert found_tournament.name == "Big Bash League"
        assert found_tournament.season_label == "2024-25"
        
    async def test_tournament_str_representation(self, test_db: AsyncSession):
        """Test tournament string representation"""
        from app.models.tournament import Tournament
        
        # Test with season_label
        tournament1 = Tournament(name="IPL", season_label="2024", match_type="T20")
        assert str(tournament1) == "IPL 2024"
        
        # Test without season_label
        tournament2 = Tournament(name="World Cup", match_type="ODI")
        assert str(tournament2) == "World Cup"
        
    async def test_tournament_dict_representation(self, test_db: AsyncSession):
        """Test tournament to_dict method"""
        from app.models.tournament import Tournament
        
        tournament = Tournament(
            name="The Ashes",
            season_label="2023",
            match_type="TEST",
            points_system={"match_win": 1},
        )
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        tournament_dict = tournament.to_dict()
        
        assert tournament_dict["public_id"] == tournament.public_id
        assert tournament_dict["name"] == "The Ashes"
        assert tournament_dict["season_label"] == "2023"
        assert tournament_dict["match_type"] == "TEST"
        assert tournament_dict["points_system"] == {"match_win": 1}
        assert "created_at" in tournament_dict


@pytest.mark.asyncio
@pytest.mark.unit
class TestTournamentMatchTypes:
    """Test Tournament match type handling"""
    
    async def test_tournament_with_various_match_types(self, test_db: AsyncSession):
        """Test creating tournaments with different match types"""
        from app.models.tournament import Tournament
        
        match_types = ["T20", "ODI", "TEST", "T10", "100BALL"]
        
        for idx, match_type in enumerate(match_types):
            tournament = Tournament(
                name=f"Tournament {idx}",
                match_type=match_type,
            )
            test_db.add(tournament)
            await test_db.commit()
            await test_db.refresh(tournament)
            
            assert tournament.match_type == match_type
            await test_db.delete(tournament)
            await test_db.commit()


@pytest.mark.asyncio
@pytest.mark.unit
class TestTournamentPointsSystem:
    """Test Tournament points system JSON handling"""
    
    async def test_tournament_with_simple_points_system(self, test_db: AsyncSession):
        """Test storing simple points system"""
        from app.models.tournament import Tournament
        
        points = {"win": 2, "loss": 0}
        tournament = Tournament(
            name="Simple League",
            match_type="T20",
            points_system=points,
        )
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.points_system == points
        assert tournament.points_system["win"] == 2
        assert tournament.points_system["loss"] == 0
        
    async def test_tournament_with_complex_points_system(self, test_db: AsyncSession):
        """Test storing complex points system with bonuses"""
        from app.models.tournament import Tournament
        
        points = {
            "win": 2,
            "loss": 0,
            "tie": 1,
            "no_result": 1,
            "bonus_batting": 1,
            "bonus_bowling": 1,
        }
        tournament = Tournament(
            name="Complex League",
            match_type="ODI",
            points_system=points,
        )
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.points_system == points
        assert tournament.points_system["bonus_batting"] == 1
        
    async def test_tournament_without_points_system(self, test_db: AsyncSession):
        """Test that points_system is optional"""
        from app.models.tournament import Tournament
        
        tournament = Tournament(
            name="Knockout Cup",
            match_type="T20",
        )
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.points_system is None


@pytest.mark.asyncio
@pytest.mark.unit
class TestTournamentTimestamps:
    """Test Tournament timestamp behavior"""
    
    async def test_created_at_auto_set(self, test_db: AsyncSession):
        """Test that created_at is automatically set"""
        from app.models.tournament import Tournament
        from datetime import datetime, timezone
        
        before = datetime.now(timezone.utc)
        tournament = Tournament(name="Test Tournament", match_type="T20")
        
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        after = datetime.now(timezone.utc)
        
        assert tournament.created_at is not None
        assert before <= tournament.created_at <= after
        
    async def test_updated_at_auto_updates(self, test_db: AsyncSession):
        """Test that updated_at is automatically updated on changes"""
        from app.models.tournament import Tournament
        import asyncio
        
        tournament = Tournament(name="Original Tournament", match_type="T20")
        test_db.add(tournament)
        await test_db.commit()
        await test_db.refresh(tournament)
        
        original_updated_at = tournament.updated_at
        
        # Wait a bit and update
        await asyncio.sleep(0.1)
        tournament.name = "Updated Tournament"
        await test_db.commit()
        await test_db.refresh(tournament)
        
        assert tournament.updated_at > original_updated_at

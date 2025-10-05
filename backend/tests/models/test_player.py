"""Tests for Player model."""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
@pytest.mark.unit
class TestPlayerModel:
    """Test Player model basic functionality"""
    
    async def test_create_player_with_required_fields(self, test_db: AsyncSession):
        """Test creating a player with only required fields"""
        from app.models.player import Player
        
        player = Player(
            full_name="Virat Kohli",
        )
        
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        
        assert player.id is not None
        assert player.public_id is not None  # Should auto-generate ULID
        assert player.full_name == "Virat Kohli"
        assert player.created_at is not None
        
    async def test_create_player_with_all_fields(self, test_db: AsyncSession):
        """Test creating a player with all optional fields"""
        from app.models.player import Player
        
        player = Player(
            full_name="Mahendra Singh Dhoni",
            known_as="MS Dhoni",
            dob=date(1981, 7, 7),
            batting_style="RHB",
            bowling_style="Right-arm medium",
        )
        
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        
        assert player.full_name == "Mahendra Singh Dhoni"
        assert player.known_as == "MS Dhoni"
        assert player.dob == date(1981, 7, 7)
        assert player.batting_style == "RHB"
        assert player.bowling_style == "Right-arm medium"
        
    async def test_player_public_id_is_unique(self, test_db: AsyncSession):
        """Test that public_id is unique across players"""
        from app.models.player import Player
        
        player1 = Player(full_name="Player One")
        player2 = Player(full_name="Player Two")
        
        test_db.add_all([player1, player2])
        await test_db.commit()
        
        assert player1.public_id != player2.public_id
        
    async def test_player_full_name_is_required(self, test_db: AsyncSession):
        """Test that full_name is required"""
        from app.models.player import Player
        
        with pytest.raises((IntegrityError, ValueError)):
            player = Player()
            test_db.add(player)
            await test_db.commit()
            
    async def test_get_player_by_public_id(self, test_db: AsyncSession):
        """Test retrieving player by public_id"""
        from app.models.player import Player
        
        player = Player(
            full_name="Rohit Sharma",
            known_as="Hitman",
        )
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        
        # Query by public_id
        result = await test_db.execute(
            select(Player).where(Player.public_id == player.public_id)
        )
        found_player = result.scalar_one()
        
        assert found_player.id == player.id
        assert found_player.full_name == "Rohit Sharma"
        assert found_player.known_as == "Hitman"
        
    async def test_player_str_representation(self, test_db: AsyncSession):
        """Test player string representation"""
        from app.models.player import Player
        
        # Test with known_as
        player1 = Player(full_name="Mahendra Singh Dhoni", known_as="MS Dhoni")
        assert str(player1) == "MS Dhoni"
        
        # Test without known_as
        player2 = Player(full_name="Virat Kohli")
        assert str(player2) == "Virat Kohli"
        
    async def test_player_dict_representation(self, test_db: AsyncSession):
        """Test player to_dict method"""
        from app.models.player import Player
        
        player = Player(
            full_name="Jasprit Bumrah",
            known_as="Boom Boom",
            dob=date(1993, 12, 6),
            batting_style="RHB",
            bowling_style="Right-arm fast",
        )
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        
        player_dict = player.to_dict()
        
        assert player_dict["public_id"] == player.public_id
        assert player_dict["full_name"] == "Jasprit Bumrah"
        assert player_dict["known_as"] == "Boom Boom"
        assert player_dict["dob"] == "1993-12-06"
        assert player_dict["batting_style"] == "RHB"
        assert player_dict["bowling_style"] == "Right-arm fast"
        assert "created_at" in player_dict
        
    async def test_player_age_calculation(self, test_db: AsyncSession):
        """Test age calculation from date of birth"""
        from app.models.player import Player
        from datetime import date
        
        # Create a player born 30 years ago
        player = Player(
            full_name="Test Player",
            dob=date(1995, 1, 1),
        )
        
        age = player.get_age()
        assert age is not None
        assert age >= 29  # Should be at least 29 (depends on current date)
        
        # Player without DOB
        player_no_dob = Player(full_name="Unknown Age")
        assert player_no_dob.get_age() is None


@pytest.mark.asyncio
@pytest.mark.unit
class TestPlayerTeamRelationship:
    """Test Player-Team many-to-many relationship through team_player"""
    
    async def test_player_has_teams_relationship(self, test_db: AsyncSession):
        """Test that player can be associated with teams"""
        from app.models.player import Player
        
        player = Player(full_name="Test Player")
        
        # Check that teams relationship exists (even if empty initially)
        assert hasattr(player, 'teams')
        
    async def test_player_team_association(self, test_db: AsyncSession):
        """Test creating player-team association through TeamPlayer"""
        from app.models.player import Player
        from app.models.team import Team
        from app.models.team_player import TeamPlayer
        
        # Create player and team
        player = Player(full_name="Virat Kohli")
        team = Team(name="Royal Challengers Bangalore", short_name="RCB")
        
        test_db.add_all([player, team])
        await test_db.commit()
        await test_db.refresh(player)
        await test_db.refresh(team)
        
        # Create association
        team_player = TeamPlayer(
            team_id=team.id,
            player_id=player.id,
            shirt_number=18,
            start_date=date(2008, 1, 1),
        )
        
        test_db.add(team_player)
        await test_db.commit()
        
        # Verify association was created
        result = await test_db.execute(
            select(TeamPlayer).where(TeamPlayer.player_id == player.id)
        )
        associations = result.scalars().all()
        
        assert len(associations) == 1
        assert associations[0].shirt_number == 18


@pytest.mark.asyncio
@pytest.mark.unit
class TestPlayerBattingBowlingStyles:
    """Test Player batting and bowling style validation"""
    
    async def test_valid_batting_styles(self, test_db: AsyncSession):
        """Test valid batting styles are accepted"""
        from app.models.player import Player
        
        valid_styles = ["RHB", "LHB"]
        
        for style in valid_styles:
            player = Player(
                full_name=f"Player {style}",
                batting_style=style,
            )
            test_db.add(player)
            await test_db.commit()
            await test_db.refresh(player)
            
            assert player.batting_style == style
            await test_db.delete(player)
            await test_db.commit()
            
    async def test_valid_bowling_styles(self, test_db: AsyncSession):
        """Test various bowling styles are accepted"""
        from app.models.player import Player
        
        valid_styles = [
            "Right-arm fast",
            "Right-arm medium",
            "Right-arm off-break",
            "Right-arm leg-break",
            "Left-arm fast",
            "Left-arm orthodox",
            "Left-arm chinaman",
        ]
        
        for style in valid_styles:
            player = Player(
                full_name=f"Player {style[:10]}",
                bowling_style=style,
            )
            test_db.add(player)
            await test_db.commit()
            await test_db.refresh(player)
            
            assert player.bowling_style == style
            await test_db.delete(player)
            await test_db.commit()


@pytest.mark.asyncio
@pytest.mark.unit
class TestPlayerTimestamps:
    """Test Player timestamp behavior"""
    
    async def test_created_at_auto_set(self, test_db: AsyncSession):
        """Test that created_at is automatically set"""
        from app.models.player import Player
        from datetime import datetime, timezone
        
        before = datetime.now(timezone.utc)
        player = Player(full_name="Test Player")
        
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        after = datetime.now(timezone.utc)
        
        assert player.created_at is not None
        assert before <= player.created_at <= after
        
    async def test_updated_at_auto_updates(self, test_db: AsyncSession):
        """Test that updated_at is automatically updated on changes"""
        from app.models.player import Player
        import asyncio
        
        player = Player(full_name="Test Player")
        test_db.add(player)
        await test_db.commit()
        await test_db.refresh(player)
        
        original_updated_at = player.updated_at
        
        # Wait a bit and update
        await asyncio.sleep(0.1)
        player.known_as = "Updated Name"
        await test_db.commit()
        await test_db.refresh(player)
        
        assert player.updated_at > original_updated_at

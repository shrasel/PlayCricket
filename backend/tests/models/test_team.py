"""
TDD Tests for Team Model
Write tests first, then implement the model
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
@pytest.mark.unit
class TestTeamModel:
    """Test Team model creation and constraints"""
    
    async def test_create_team_with_required_fields(self, test_db: AsyncSession):
        """Test creating a team with all required fields"""
        from app.models.team import Team
        
        team = Team(
            name="Mumbai Indians",
            short_name="MI",
            country_code="IND",
        )
        
        test_db.add(team)
        await test_db.commit()
        await test_db.refresh(team)
        
        assert team.id is not None
        assert team.public_id is not None  # Should auto-generate ULID
        assert team.name == "Mumbai Indians"
        assert team.short_name == "MI"
        assert team.country_code == "IND"
        assert team.created_at is not None
    
    async def test_team_public_id_is_unique(self, test_db: AsyncSession):
        """Test that public_id is unique across teams"""
        from app.models.team import Team
        
        team1 = Team(name="Team 1", short_name="T1")
        team2 = Team(name="Team 2", short_name="T2")
        
        test_db.add_all([team1, team2])
        await test_db.commit()
        
        assert team1.public_id != team2.public_id
    
    async def test_team_name_must_be_unique(self, test_db: AsyncSession):
        """Test that team name must be unique"""
        from app.models.team import Team
        
        team1 = Team(name="Mumbai Indians", short_name="MI")
        test_db.add(team1)
        await test_db.commit()
        
        # Try to create another team with same name
        team2 = Team(name="Mumbai Indians", short_name="MI2")
        test_db.add(team2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()
    
    async def test_team_short_name_must_be_unique(self, test_db: AsyncSession):
        """Test that short_name must be unique"""
        from app.models.team import Team
        
        team1 = Team(name="Mumbai Indians", short_name="MI")
        test_db.add(team1)
        await test_db.commit()
        
        # Try to create another team with same short_name
        team2 = Team(name="Mumbai Indians 2", short_name="MI")
        test_db.add(team2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()
    
    async def test_team_with_optional_fields(self, test_db: AsyncSession):
        """Test creating team with all optional fields"""
        from app.models.team import Team
        
        team = Team(
            name="Chennai Super Kings",
            short_name="CSK",
            country_code="IND",
            logo_url="https://example.com/csk-logo.png",
            primary_color="#FDB913",
            secondary_color="#00A651",
        )
        
        test_db.add(team)
        await test_db.commit()
        await test_db.refresh(team)
        
        assert team.logo_url == "https://example.com/csk-logo.png"
        assert team.primary_color == "#FDB913"
        assert team.secondary_color == "#00A651"
    
    async def test_get_team_by_public_id(self, test_db: AsyncSession):
        """Test retrieving team by public_id"""
        from app.models.team import Team
        
        team = Team(name="Royal Challengers Bangalore", short_name="RCB")
        test_db.add(team)
        await test_db.commit()
        await test_db.refresh(team)
        
        # Query by public_id
        result = await test_db.execute(
            select(Team).where(Team.public_id == team.public_id)
        )
        found_team = result.scalar_one_or_none()
        
        assert found_team is not None
        assert found_team.id == team.id
        assert found_team.name == "Royal Challengers Bangalore"
    
    async def test_team_str_representation(self, test_db: AsyncSession):
        """Test team string representation"""
        from app.models.team import Team
        
        team = Team(name="Kolkata Knight Riders", short_name="KKR")
        
        assert str(team) == "Kolkata Knight Riders (KKR)"
    
    async def test_team_dict_representation(self, test_db: AsyncSession):
        """Test team to_dict method"""
        from app.models.team import Team
        
        team = Team(
            name="Delhi Capitals",
            short_name="DC",
            country_code="IND",
        )
        test_db.add(team)
        await test_db.commit()
        await test_db.refresh(team)
        
        team_dict = team.to_dict()
        
        assert team_dict["public_id"] == team.public_id
        assert team_dict["name"] == "Delhi Capitals"
        assert team_dict["short_name"] == "DC"
        assert team_dict["country_code"] == "IND"
        assert "created_at" in team_dict


@pytest.mark.asyncio
@pytest.mark.unit
class TestTeamRelationships:
    """Test Team relationships with other models"""
    
    async def test_team_has_players_relationship(self, test_db: AsyncSession):
        """Test that team can have multiple players"""
        from app.models.team import Team
        # TODO: Implement when Player model exists
        pass
    
    async def test_team_has_tournament_relationship(self, test_db: AsyncSession):
        """Test that team can participate in tournaments"""
        from app.models.team import Team
        # TODO: Implement when Tournament model exists
        pass
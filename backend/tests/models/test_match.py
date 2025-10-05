"""Tests for Match-related models."""
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
@pytest.mark.unit
class TestMatchModel:
    """Test Match model basic functionality"""
    
    async def test_create_match_with_required_fields(self, test_db: AsyncSession):
        """Test creating a match with only required fields"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        # Create venue first
        venue = Venue(name="Test Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6,
        )
        
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        
        assert match.id is not None
        assert match.public_id is not None  # Should auto-generate ULID
        assert match.venue_id == venue.id
        assert match.match_type == "T20"
        assert match.status == "SCHEDULED"
        assert match.balls_per_over == 6
        assert match.created_at is not None
        
    async def test_create_match_with_all_fields(self, test_db: AsyncSession):
        """Test creating a match with all optional fields"""
        from app.models.match import Match
        from app.models.venue import Venue
        from app.models.tournament import Tournament
        
        # Create dependencies
        venue = Venue(name="Lord's")
        tournament = Tournament(name="World Cup", match_type="ODI")
        test_db.add_all([venue, tournament])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(tournament)
        
        start_time = datetime(2024, 10, 15, 10, 30, tzinfo=timezone.utc)
        
        match = Match(
            venue_id=venue.id,
            tournament_id=tournament.id,
            match_type="ODI",
            status="LIVE",
            start_time=start_time,
            local_tz="Asia/Kolkata",
            overs_limit=50,
            balls_per_over=6,
            notes="Important match",
        )
        
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        
        assert match.tournament_id == tournament.id
        assert match.start_time == start_time
        assert match.local_tz == "Asia/Kolkata"
        assert match.overs_limit == 50
        assert match.notes == "Important match"
        
    async def test_match_public_id_is_unique(self, test_db: AsyncSession):
        """Test that public_id is unique across matches"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        match1 = Match(venue_id=venue.id, match_type="T20", status="SCHEDULED", balls_per_over=6)
        match2 = Match(venue_id=venue.id, match_type="ODI", status="SCHEDULED", balls_per_over=6)
        
        test_db.add_all([match1, match2])
        await test_db.commit()
        
        assert match1.public_id != match2.public_id
        
    async def test_match_status_values(self, test_db: AsyncSession):
        """Test various match status values"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        statuses = ["SCHEDULED", "LIVE", "COMPLETED", "ABANDONED", "CANCELLED"]
        
        for status in statuses:
            match = Match(
                venue_id=venue.id,
                match_type="T20",
                status=status,
                balls_per_over=6,
            )
            test_db.add(match)
            await test_db.commit()
            await test_db.refresh(match)
            
            assert match.status == status
            await test_db.delete(match)
            await test_db.commit()
            
    async def test_match_types(self, test_db: AsyncSession):
        """Test various match types"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        match_types = ["T20", "ODI", "TEST", "T10", "100BALL"]
        
        for match_type in match_types:
            match = Match(
                venue_id=venue.id,
                match_type=match_type,
                status="SCHEDULED",
                balls_per_over=6,
            )
            test_db.add(match)
            await test_db.commit()
            await test_db.refresh(match)
            
            assert match.match_type == match_type
            await test_db.delete(match)
            await test_db.commit()
            
    async def test_match_overs_limit(self, test_db: AsyncSession):
        """Test overs limit for limited overs matches"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        # Test with overs limit (ODI/T20)
        match1 = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            overs_limit=20,
            balls_per_over=6,
        )
        test_db.add(match1)
        await test_db.commit()
        await test_db.refresh(match1)
        assert match1.overs_limit == 20
        
        # Test without overs limit (TEST)
        match2 = Match(
            venue_id=venue.id,
            match_type="TEST",
            status="SCHEDULED",
            balls_per_over=6,
        )
        test_db.add(match2)
        await test_db.commit()
        await test_db.refresh(match2)
        assert match2.overs_limit is None
        
    async def test_match_str_representation(self, test_db: AsyncSession):
        """Test match string representation"""
        from app.models.match import Match
        from app.models.venue import Venue
        from app.models.tournament import Tournament
        
        venue = Venue(name="MCG")
        tournament = Tournament(name="BBL", match_type="T20")
        test_db.add_all([venue, tournament])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(tournament)
        
        match = Match(
            venue_id=venue.id,
            tournament_id=tournament.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6,
        )
        
        assert "MCG" in str(match) or "T20" in str(match)


@pytest.mark.asyncio
@pytest.mark.unit
class TestMatchTeamRelationship:
    """Test Match-Team relationship through MatchTeam"""
    
    async def test_match_team_association(self, test_db: AsyncSession):
        """Test creating match-team association"""
        from app.models.match import Match, MatchTeam
        from app.models.team import Team
        from app.models.venue import Venue
        
        # Create dependencies
        venue = Venue(name="Stadium")
        team1 = Team(name="Team A", short_name="TA")
        team2 = Team(name="Team B", short_name="TB")
        test_db.add_all([venue, team1, team2])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(team1)
        await test_db.refresh(team2)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6,
        )
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        
        # Create match-team associations
        mt1 = MatchTeam(match_id=match.id, team_id=team1.id, is_home=True)
        mt2 = MatchTeam(match_id=match.id, team_id=team2.id, is_home=False)
        
        test_db.add_all([mt1, mt2])
        await test_db.commit()
        
        # Verify associations
        result = await test_db.execute(
            select(MatchTeam).where(MatchTeam.match_id == match.id)
        )
        associations = result.scalars().all()
        
        assert len(associations) == 2
        assert any(a.team_id == team1.id and a.is_home for a in associations)
        assert any(a.team_id == team2.id and not a.is_home for a in associations)
        
    async def test_match_team_unique_constraint(self, test_db: AsyncSession):
        """Test that same team cannot be added twice to same match"""
        from app.models.match import Match, MatchTeam
        from app.models.team import Team
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        team = Team(name="Team A", short_name="TA")
        test_db.add_all([venue, team])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(team)
        
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6,
        )
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        
        # Add team to match
        mt1 = MatchTeam(match_id=match.id, team_id=team.id, is_home=True)
        test_db.add(mt1)
        await test_db.commit()
        
        # Try to add same team again
        mt2 = MatchTeam(match_id=match.id, team_id=team.id, is_home=False)
        test_db.add(mt2)
        
        with pytest.raises(IntegrityError):
            await test_db.commit()


@pytest.mark.asyncio
@pytest.mark.unit
class TestMatchToss:
    """Test Match toss information"""
    
    async def test_match_toss_creation(self, test_db: AsyncSession):
        """Test creating match toss record"""
        from app.models.match import Match, MatchToss
        from app.models.team import Team
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        team = Team(name="India", short_name="IND")
        test_db.add_all([venue, team])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(team)
        
        match = Match(
            venue_id=venue.id,
            match_type="ODI",
            status="LIVE",
            balls_per_over=6,
        )
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        
        # Create toss record
        toss = MatchToss(
            match_id=match.id,
            won_by_team_id=team.id,
            decision="BAT",
        )
        test_db.add(toss)
        await test_db.commit()
        await test_db.refresh(toss)
        
        assert toss.match_id == match.id
        assert toss.won_by_team_id == team.id
        assert toss.decision == "BAT"
        
    async def test_match_toss_decision_values(self, test_db: AsyncSession):
        """Test toss decision values (BAT/BOWL)"""
        from app.models.match import Match, MatchToss
        from app.models.team import Team
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        team = Team(name="Team", short_name="TM")
        test_db.add_all([venue, team])
        await test_db.commit()
        await test_db.refresh(venue)
        await test_db.refresh(team)
        
        for decision in ["BAT", "BOWL"]:
            match = Match(
                venue_id=venue.id,
                match_type="T20",
                status="LIVE",
                balls_per_over=6,
            )
            test_db.add(match)
            await test_db.commit()
            await test_db.refresh(match)
            
            toss = MatchToss(
                match_id=match.id,
                won_by_team_id=team.id,
                decision=decision,
            )
            test_db.add(toss)
            await test_db.commit()
            await test_db.refresh(toss)
            
            assert toss.decision == decision


@pytest.mark.asyncio
@pytest.mark.unit
class TestMatchTimestamps:
    """Test Match timestamp behavior"""
    
    async def test_created_at_auto_set(self, test_db: AsyncSession):
        """Test that created_at is automatically set"""
        from app.models.match import Match
        from app.models.venue import Venue
        
        venue = Venue(name="Stadium")
        test_db.add(venue)
        await test_db.commit()
        await test_db.refresh(venue)
        
        before = datetime.now(timezone.utc)
        match = Match(
            venue_id=venue.id,
            match_type="T20",
            status="SCHEDULED",
            balls_per_over=6,
        )
        
        test_db.add(match)
        await test_db.commit()
        await test_db.refresh(match)
        after = datetime.now(timezone.utc)
        
        assert match.created_at is not None
        assert before <= match.created_at <= after

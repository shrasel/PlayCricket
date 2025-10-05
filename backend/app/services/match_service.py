"""Match service for business logic."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.match import Match, MatchTeam, MatchToss
from app.services.base_service import BaseService


class MatchService(BaseService[Match]):
    """Service for Match operations."""
    
    def __init__(self):
        """Initialize MatchService."""
        super().__init__(Match)
    
    async def get_match_with_full_details(
        self,
        db: AsyncSession,
        public_id: str
    ) -> Optional[Match]:
        """Get match with all relationships loaded."""
        query = select(Match).where(Match.public_id == public_id).options(
            selectinload(Match.venue),
            selectinload(Match.tournament),
            selectinload(Match.match_teams).selectinload(MatchTeam.team),
            selectinload(Match.match_toss).selectinload(MatchToss.toss_winner),
            selectinload(Match.winning_team),
            selectinload(Match.innings)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_status(
        self,
        db: AsyncSession,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get matches by status."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"status": status},
            order_by="scheduled_start",
            order_desc=True
        )
    
    async def get_live_matches(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get currently live matches."""
        return await self.get_by_status(db, "LIVE", skip=skip, limit=limit)
    
    async def get_by_tournament(
        self,
        db: AsyncSession,
        tournament_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get matches by tournament."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"tournament_id": tournament_id},
            order_by="scheduled_start"
        )
    
    async def get_by_venue(
        self,
        db: AsyncSession,
        venue_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get matches by venue."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"venue_id": venue_id},
            order_by="scheduled_start",
            order_desc=True
        )
    
    async def get_by_team(
        self,
        db: AsyncSession,
        team_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get matches involving a specific team."""
        query = select(Match).join(MatchTeam).where(
            MatchTeam.team_id == team_id
        ).order_by(Match.scheduled_start.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_matches_between_dates(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """Get matches between two dates."""
        query = select(Match).where(
            and_(
                Match.scheduled_start >= start_date,
                Match.scheduled_start <= end_date
            )
        ).order_by(Match.scheduled_start).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_match_status(
        self,
        db: AsyncSession,
        match: Match,
        new_status: str
    ) -> Match:
        """Update match status."""
        match.status = new_status
        
        # Set actual_start when match goes live
        if new_status == "LIVE" and match.actual_start is None:
            match.actual_start = datetime.utcnow()
        
        # Set end_time when match completes
        if new_status in ["COMPLETED", "ABANDONED", "CANCELLED"] and match.end_time is None:
            match.end_time = datetime.utcnow()
        
        await db.flush()
        await db.refresh(match)
        return match
    
    async def set_match_result(
        self,
        db: AsyncSession,
        match: Match,
        winning_team_id: int,
        result_type: str,
        result_margin: str
    ) -> Match:
        """Set match result."""
        match.winning_team_id = winning_team_id
        match.result_type = result_type
        match.result_margin = result_margin
        match.status = "COMPLETED"
        
        if match.end_time is None:
            match.end_time = datetime.utcnow()
        
        await db.flush()
        await db.refresh(match)
        return match
    
    async def create_match_with_teams(
        self,
        db: AsyncSession,
        match_data: dict,
        team_ids: List[int],
        is_home_flags: List[bool]
    ) -> Match:
        """Create match with associated teams."""
        # Create match
        match = await self.create(db, **match_data)
        
        # Create match-team associations
        for team_id, is_home in zip(team_ids, is_home_flags):
            match_team = MatchTeam(
                match_id=match.id,
                team_id=team_id,
                is_home=is_home
            )
            db.add(match_team)
        
        await db.flush()
        await db.refresh(match)
        return match
    
    async def set_match_toss(
        self,
        db: AsyncSession,
        match: Match,
        toss_winner_id: int,
        elected_to: str
    ) -> Match:
        """Set or update match toss."""
        # Check if toss already exists
        existing_toss = await db.execute(
            select(MatchToss).where(MatchToss.match_id == match.id)
        )
        toss = existing_toss.scalar_one_or_none()
        
        if toss:
            # Update existing
            toss.toss_winner_id = toss_winner_id
            toss.elected_to = elected_to
        else:
            # Create new
            toss = MatchToss(
                match_id=match.id,
                toss_winner_id=toss_winner_id,
                elected_to=elected_to
            )
            db.add(toss)
        
        await db.flush()
        await db.refresh(match)
        return match


# Singleton instance
match_service = MatchService()

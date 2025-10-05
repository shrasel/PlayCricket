"""Tournament service for business logic."""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.tournament import Tournament
from app.services.base_service import BaseService


class TournamentService(BaseService[Tournament]):
    """Service for Tournament operations."""
    
    def __init__(self):
        """Initialize TournamentService."""
        super().__init__(Tournament)
    
    async def get_by_name_and_season(
        self,
        db: AsyncSession,
        name: str,
        season: str
    ) -> Optional[Tournament]:
        """Get tournament by name and season."""
        query = select(Tournament).where(
            and_(
                Tournament.name == name,
                Tournament.season == season
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_match_type(
        self,
        db: AsyncSession,
        match_type: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """Get tournaments by match type."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"match_type": match_type},
            order_by="start_date",
            order_desc=True
        )
    
    async def get_active_tournaments(
        self,
        db: AsyncSession,
        today: Optional[date] = None,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """Get currently active tournaments."""
        if today is None:
            today = date.today()
        
        query = select(Tournament).where(
            and_(
                Tournament.start_date <= today,
                Tournament.end_date >= today
            )
        ).order_by(Tournament.start_date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_upcoming_tournaments(
        self,
        db: AsyncSession,
        today: Optional[date] = None,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """Get upcoming tournaments."""
        if today is None:
            today = date.today()
        
        query = select(Tournament).where(
            Tournament.start_date > today
        ).order_by(Tournament.start_date).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def search_tournaments(
        self,
        db: AsyncSession,
        search_term: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """Search tournaments by name or short name."""
        return await self.search(
            db,
            search_term=search_term,
            search_fields=["name", "short_name"],
            skip=skip,
            limit=limit
        )


# Singleton instance
tournament_service = TournamentService()

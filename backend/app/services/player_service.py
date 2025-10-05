"""Player service for business logic."""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.player import Player
from app.services.base_service import BaseService


class PlayerService(BaseService[Player]):
    """Service for Player operations."""
    
    def __init__(self):
        """Initialize PlayerService."""
        super().__init__(Player)
    
    async def get_by_full_name(
        self,
        db: AsyncSession,
        full_name: str
    ) -> Optional[Player]:
        """Get player by exact full name."""
        query = select(Player).where(Player.full_name == full_name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def search_players(
        self,
        db: AsyncSession,
        search_term: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Player]:
        """Search players by full name or known as."""
        return await self.search(
            db,
            search_term=search_term,
            search_fields=["full_name", "known_as"],
            skip=skip,
            limit=limit
        )
    
    async def get_by_batting_style(
        self,
        db: AsyncSession,
        batting_style: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Player]:
        """Get players by batting style."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"batting_style": batting_style}
        )
    
    async def get_by_bowling_style(
        self,
        db: AsyncSession,
        bowling_style: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Player]:
        """Get players by bowling style."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"bowling_style": bowling_style}
        )
    
    async def get_by_age_range(
        self,
        db: AsyncSession,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Player]:
        """Get players within age range."""
        query = select(Player)
        
        today = date.today()
        
        if min_age is not None:
            # Calculate max birth date for min age
            max_birth_date = today.replace(year=today.year - min_age)
            query = query.where(Player.dob <= max_birth_date)
        
        if max_age is not None:
            # Calculate min birth date for max age
            min_birth_date = today.replace(year=today.year - max_age - 1)
            query = query.where(Player.dob >= min_birth_date)
        
        query = query.order_by(Player.dob.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())


# Singleton instance
player_service = PlayerService()

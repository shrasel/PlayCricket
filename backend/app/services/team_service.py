"""Team service for business logic."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.team import Team
from app.services.base_service import BaseService


class TeamService(BaseService[Team]):
    """Service for Team operations."""
    
    def __init__(self):
        """Initialize TeamService."""
        super().__init__(Team)
    
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Team]:
        """Get team by exact name."""
        query = select(Team).where(Team.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_country_code(
        self,
        db: AsyncSession,
        country_code: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Team]:
        """Get teams by country code."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"country_code": country_code}
        )
    
    async def search_teams(
        self,
        db: AsyncSession,
        search_term: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Team]:
        """Search teams by name or short name."""
        return await self.search(
            db,
            search_term=search_term,
            search_fields=["name", "short_name"],
            skip=skip,
            limit=limit
        )


# Singleton instance
team_service = TeamService()

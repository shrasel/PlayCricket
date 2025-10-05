"""Venue service for business logic."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.venue import Venue
from app.services.base_service import BaseService


class VenueService(BaseService[Venue]):
    """Service for Venue operations."""
    
    def __init__(self):
        """Initialize VenueService."""
        super().__init__(Venue)
    
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Venue]:
        """Get venue by exact name."""
        query = select(Venue).where(Venue.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_city(
        self,
        db: AsyncSession,
        city: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Venue]:
        """Get venues by city."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"city": city}
        )
    
    async def get_by_country_code(
        self,
        db: AsyncSession,
        country_code: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Venue]:
        """Get venues by country code."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"country_code": country_code}
        )
    
    async def search_venues(
        self,
        db: AsyncSession,
        search_term: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Venue]:
        """Search venues by name or city."""
        return await self.search(
            db,
            search_term=search_term,
            search_fields=["name", "city"],
            skip=skip,
            limit=limit
        )


# Singleton instance
venue_service = VenueService()

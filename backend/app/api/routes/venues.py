"""Venue API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.venue_service import venue_service
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse, VenueSummary
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post(
    "",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new venue"
)
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cricket venue."""
    # Check if venue with same name already exists
    existing_venue = await venue_service.get_by_name(db, venue_data.name)
    if existing_venue:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Venue with name '{venue_data.name}' already exists"
        )
    
    venue = await venue_service.create(db, **venue_data.model_dump())
    await db.commit()
    return venue


@router.get(
    "",
    response_model=PaginatedResponse[VenueSummary],
    summary="List all venues"
)
async def list_venues(
    pagination: PaginationParams = Depends(),
    city: str = Query(None, description="Filter by city"),
    country_code: str = Query(None, description="Filter by country code"),
    search: str = Query(None, description="Search by name or city"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of venues."""
    filters = {}
    if city:
        filters["city"] = city
    if country_code:
        filters["country_code"] = country_code
    
    if search:
        venues = await venue_service.search_venues(
            db,
            search_term=search,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(venues)
    else:
        venues = await venue_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters if filters else None
        )
        total = await venue_service.count(db, filters=filters if filters else None)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=venues
    )


@router.get(
    "/{venue_id}",
    response_model=VenueResponse,
    summary="Get venue by ID"
)
async def get_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific venue by public ID."""
    venue = await venue_service.get_by_public_id(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with ID '{venue_id}' not found"
        )
    return venue


@router.patch(
    "/{venue_id}",
    response_model=VenueResponse,
    summary="Update venue"
)
async def update_venue(
    venue_id: str,
    venue_data: VenueUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a venue's information."""
    venue = await venue_service.get_by_public_id(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with ID '{venue_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = venue_data.model_dump(exclude_unset=True)
    
    venue = await venue_service.update(db, obj=venue, update_data=update_data)
    await db.commit()
    return venue


@router.delete(
    "/{venue_id}",
    response_model=MessageResponse,
    summary="Delete venue"
)
async def delete_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a venue."""
    venue = await venue_service.get_by_public_id(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with ID '{venue_id}' not found"
        )
    
    await venue_service.delete(db, obj=venue)
    await db.commit()
    
    return MessageResponse(
        message=f"Venue '{venue.name}' deleted successfully"
    )

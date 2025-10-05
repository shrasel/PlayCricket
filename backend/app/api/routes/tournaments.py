"""Tournament API endpoints."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.tournament_service import tournament_service
from app.schemas.tournament import TournamentCreate, TournamentUpdate, TournamentResponse, TournamentSummary
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


@router.post(
    "",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tournament"
)
async def create_tournament(
    tournament_data: TournamentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cricket tournament."""
    tournament = await tournament_service.create(db, **tournament_data.model_dump())
    await db.commit()
    return tournament


@router.get(
    "",
    response_model=PaginatedResponse[TournamentSummary],
    summary="List all tournaments"
)
async def list_tournaments(
    pagination: PaginationParams = Depends(),
    match_type: str = Query(None, description="Filter by match type (T20, ODI, TEST, etc.)"),
    status: str = Query(None, description="Filter by status (active, upcoming)"),
    search: str = Query(None, description="Search by name or short name"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of tournaments."""
    if search:
        tournaments = await tournament_service.search_tournaments(
            db,
            search_term=search,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(tournaments)
    elif status == "active":
        tournaments = await tournament_service.get_active_tournaments(
            db,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(tournaments)
    elif status == "upcoming":
        tournaments = await tournament_service.get_upcoming_tournaments(
            db,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(tournaments)
    else:
        filters = {}
        if match_type:
            filters["match_type"] = match_type
        
        tournaments = await tournament_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters if filters else None,
            order_by="start_date",
            order_desc=True
        )
        total = await tournament_service.count(db, filters=filters if filters else None)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=tournaments
    )


@router.get(
    "/{tournament_id}",
    response_model=TournamentResponse,
    summary="Get tournament by ID"
)
async def get_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tournament by public ID."""
    tournament = await tournament_service.get_by_public_id(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID '{tournament_id}' not found"
        )
    return tournament


@router.patch(
    "/{tournament_id}",
    response_model=TournamentResponse,
    summary="Update tournament"
)
async def update_tournament(
    tournament_id: str,
    tournament_data: TournamentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a tournament's information."""
    tournament = await tournament_service.get_by_public_id(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID '{tournament_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = tournament_data.model_dump(exclude_unset=True)
    
    tournament = await tournament_service.update(db, obj=tournament, update_data=update_data)
    await db.commit()
    return tournament


@router.delete(
    "/{tournament_id}",
    response_model=MessageResponse,
    summary="Delete tournament"
)
async def delete_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tournament."""
    tournament = await tournament_service.get_by_public_id(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID '{tournament_id}' not found"
        )
    
    await tournament_service.delete(db, obj=tournament)
    await db.commit()
    
    return MessageResponse(
        message=f"Tournament '{tournament.name}' deleted successfully"
    )

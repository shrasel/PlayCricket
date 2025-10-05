"""Player API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.player_service import player_service
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerSummary
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/players", tags=["Players"])


@router.post(
    "",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new player"
)
async def create_player(
    player_data: PlayerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cricket player."""
    # Check if player with same full name already exists
    existing_player = await player_service.get_by_full_name(db, player_data.full_name)
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player with name '{player_data.full_name}' already exists"
        )
    
    player = await player_service.create(db, **player_data.model_dump())
    await db.commit()
    return player


@router.get(
    "",
    response_model=PaginatedResponse[PlayerSummary],
    summary="List all players"
)
async def list_players(
    pagination: PaginationParams = Depends(),
    search: str = Query(None, description="Search by full name or known as"),
    batting_style: str = Query(None, description="Filter by batting style"),
    bowling_style: str = Query(None, description="Filter by bowling style"),
    min_age: Optional[int] = Query(None, ge=0, description="Minimum age"),
    max_age: Optional[int] = Query(None, ge=0, description="Maximum age"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of players."""
    if search:
        players = await player_service.search_players(
            db,
            search_term=search,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(players)
    elif min_age is not None or max_age is not None:
        players = await player_service.get_by_age_range(
            db,
            min_age=min_age,
            max_age=max_age,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(players)
    else:
        filters = {}
        if batting_style:
            filters["batting_style"] = batting_style
        if bowling_style:
            filters["bowling_style"] = bowling_style
        
        players = await player_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters if filters else None
        )
        total = await player_service.count(db, filters=filters if filters else None)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=players
    )


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Get player by ID"
)
async def get_player(
    player_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific player by public ID."""
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    return player


@router.patch(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Update player"
)
async def update_player(
    player_id: str,
    player_data: PlayerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a player's information."""
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = player_data.model_dump(exclude_unset=True)
    
    player = await player_service.update(db, obj=player, update_data=update_data)
    await db.commit()
    return player


@router.delete(
    "/{player_id}",
    response_model=MessageResponse,
    summary="Delete player"
)
async def delete_player(
    player_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a player."""
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    
    await player_service.delete(db, obj=player)
    await db.commit()
    
    return MessageResponse(
        message=f"Player '{player.full_name}' deleted successfully"
    )

"""Team API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.team_service import team_service
from app.services.player_service import player_service
from app.services.venue_service import venue_service
from app.services.tournament_service import tournament_service
from app.services.match_service import match_service
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamSummary
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team"
)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cricket team."""
    # Check if team with same name already exists
    existing_team = await team_service.get_by_name(db, team_data.name)
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team with name '{team_data.name}' already exists"
        )
    
    team = await team_service.create(db, **team_data.model_dump())
    await db.commit()
    return team


@router.get(
    "",
    response_model=PaginatedResponse[TeamSummary],
    summary="List all teams"
)
async def list_teams(
    pagination: PaginationParams = Depends(),
    country_code: str = Query(None, description="Filter by country code"),
    search: str = Query(None, description="Search by name or short name"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of teams."""
    filters = {}
    if country_code:
        filters["country_code"] = country_code
    
    if search:
        teams = await team_service.search_teams(
            db,
            search_term=search,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(teams)
    else:
        teams = await team_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters if filters else None
        )
        total = await team_service.count(db, filters=filters if filters else None)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=teams
    )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team by ID"
)
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific team by public ID."""
    team = await team_service.get_by_public_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID '{team_id}' not found"
        )
    return team


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team"
)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a team's information."""
    team = await team_service.get_by_public_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID '{team_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = team_data.model_dump(exclude_unset=True)
    
    team = await team_service.update(db, obj=team, update_data=update_data)
    await db.commit()
    return team


@router.delete(
    "/{team_id}",
    response_model=MessageResponse,
    summary="Delete team"
)
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a team."""
    team = await team_service.get_by_public_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID '{team_id}' not found"
        )
    
    await team_service.delete(db, obj=team)
    await db.commit()
    
    return MessageResponse(
        message=f"Team '{team.name}' deleted successfully"
    )

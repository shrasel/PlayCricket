"""Match API endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.match_service import match_service
from app.services.team_service import team_service
from app.services.venue_service import venue_service
from app.services.tournament_service import tournament_service
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchResponse, MatchSummary,
    MatchTossUpdate
)
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new match"
)
async def create_match(
    match_data: MatchCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cricket match with teams."""
    # Validate venue exists
    venue = await venue_service.get_by_public_id(db, match_data.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with ID '{match_data.venue_id}' not found"
        )
    
    # Validate tournament if provided
    tournament_id = None
    if match_data.tournament_id:
        tournament = await tournament_service.get_by_public_id(db, match_data.tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID '{match_data.tournament_id}' not found"
            )
        tournament_id = tournament.id
    
    # Validate teams
    if len(match_data.teams) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly 2 teams are required for a match"
        )
    
    team_ids = []
    is_home_flags = []
    for team_data in match_data.teams:
        team = await team_service.get_by_public_id(db, team_data.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID '{team_data.team_id}' not found"
            )
        team_ids.append(team.id)
        is_home_flags.append(team_data.is_home)
    
    # Prepare match data - exclude venue_id and tournament_id as we'll use internal IDs
    match_dict = match_data.model_dump(exclude={"teams", "toss", "venue_id", "tournament_id"})
    match_dict["venue_id"] = venue.id
    match_dict["tournament_id"] = tournament_id
    
    # Create match with teams
    match = await match_service.create_match_with_teams(
        db,
        match_data=match_dict,
        team_ids=team_ids,
        is_home_flags=is_home_flags
    )
    
    # Set toss if provided
    if match_data.toss:
        toss_winner = await team_service.get_by_public_id(db, match_data.toss.toss_winner_id)
        if not toss_winner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Toss winner team with ID '{match_data.toss.toss_winner_id}' not found"
            )
        
        await match_service.set_match_toss(
            db,
            match=match,
            toss_winner_id=toss_winner.id,
            elected_to=match_data.toss.elected_to
        )
    
    await db.commit()
    
    # Return match with full details
    match = await match_service.get_match_with_full_details(db, match.public_id)
    return match


@router.get(
    "",
    response_model=PaginatedResponse[MatchSummary],
    summary="List all matches"
)
async def list_matches(
    pagination: PaginationParams = Depends(),
    status: str = Query(None, description="Filter by status (SCHEDULED, LIVE, COMPLETED, etc.)"),
    tournament_id: str = Query(None, description="Filter by tournament ID"),
    venue_id: str = Query(None, description="Filter by venue ID"),
    team_id: str = Query(None, description="Filter by team ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by start date (to)"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of matches."""
    if status:
        matches = await match_service.get_by_status(
            db,
            status=status,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(matches)
    elif tournament_id:
        tournament = await tournament_service.get_by_public_id(db, tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID '{tournament_id}' not found"
            )
        matches = await match_service.get_by_tournament(
            db,
            tournament_id=tournament.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(matches)
    elif venue_id:
        venue = await venue_service.get_by_public_id(db, venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venue with ID '{venue_id}' not found"
            )
        matches = await match_service.get_by_venue(
            db,
            venue_id=venue.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(matches)
    elif team_id:
        team = await team_service.get_by_public_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID '{team_id}' not found"
            )
        matches = await match_service.get_by_team(
            db,
            team_id=team.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(matches)
    elif start_date and end_date:
        matches = await match_service.get_matches_between_dates(
            db,
            start_date=start_date,
            end_date=end_date,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(matches)
    else:
        matches = await match_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            order_by="start_time",
            order_desc=True
        )
        total = await match_service.count(db)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=matches
    )


@router.get(
    "/live",
    response_model=PaginatedResponse[MatchSummary],
    summary="Get live matches"
)
async def get_live_matches(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get currently live matches."""
    matches = await match_service.get_live_matches(
        db,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return PaginatedResponse(
        total=len(matches),
        skip=pagination.skip,
        limit=pagination.limit,
        items=matches
    )


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Get match by ID"
)
async def get_match(
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific match by public ID with full details."""
    match = await match_service.get_match_with_full_details(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    return match


@router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Update match"
)
async def update_match(
    match_id: str,
    match_data: MatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a match's information."""
    match = await match_service.get_by_public_id(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = match_data.model_dump(exclude_unset=True)
    
    # Validate and convert IDs if provided
    if "venue_id" in update_data and update_data["venue_id"]:
        venue = await venue_service.get_by_public_id(db, update_data["venue_id"])
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venue with ID '{update_data['venue_id']}' not found"
            )
        update_data["venue_id"] = venue.id
    
    if "tournament_id" in update_data and update_data["tournament_id"]:
        tournament = await tournament_service.get_by_public_id(db, update_data["tournament_id"])
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament with ID '{update_data['tournament_id']}' not found"
            )
        update_data["tournament_id"] = tournament.id
    
    match = await match_service.update(db, obj=match, update_data=update_data)
    await db.commit()
    
    # Return with full details
    match = await match_service.get_match_with_full_details(db, match.public_id)
    return match


@router.patch(
    "/{match_id}/status",
    response_model=MatchResponse,
    summary="Update match status"
)
async def update_match_status(
    match_id: str,
    new_status: str = Query(..., description="New status (SCHEDULED, LIVE, COMPLETED, ABANDONED, CANCELLED)"),
    db: AsyncSession = Depends(get_db)
):
    """Update a match's status."""
    match = await match_service.get_by_public_id(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    valid_statuses = ["SCHEDULED", "LIVE", "COMPLETED", "ABANDONED", "CANCELLED"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    match = await match_service.update_match_status(db, match, new_status)
    await db.commit()
    
    # Return with full details
    match = await match_service.get_match_with_full_details(db, match.public_id)
    return match


@router.post(
    "/{match_id}/toss",
    response_model=MatchResponse,
    summary="Set match toss"
)
async def set_match_toss(
    match_id: str,
    toss_data: MatchTossUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Set or update the match toss."""
    match = await match_service.get_by_public_id(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    # Validate toss winner team
    toss_winner = await team_service.get_by_public_id(db, toss_data.toss_winner_id)
    if not toss_winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Toss winner team with ID '{toss_data.toss_winner_id}' not found"
        )
    
    # Validate elected_to
    if toss_data.elected_to not in ["BAT", "BOWL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="elected_to must be either 'BAT' or 'BOWL'"
        )
    
    match = await match_service.set_match_toss(
        db,
        match=match,
        toss_winner_id=toss_winner.id,
        elected_to=toss_data.elected_to
    )
    await db.commit()
    
    # Return with full details
    match = await match_service.get_match_with_full_details(db, match.public_id)
    return match


@router.delete(
    "/{match_id}",
    response_model=MessageResponse,
    summary="Delete match"
)
async def delete_match(
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a match."""
    match = await match_service.get_by_public_id(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    await match_service.delete(db, obj=match)
    await db.commit()
    
    return MessageResponse(
        message=f"Match deleted successfully"
    )

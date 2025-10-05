"""Innings API endpoints."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.innings_service import innings_service
from app.services.match_service import match_service
from app.services.team_service import team_service
from app.schemas.innings import InningsCreate, InningsUpdate, InningsResponse, InningsSummary
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/innings", tags=["Innings"])


@router.post(
    "",
    response_model=InningsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new innings"
)
async def create_innings(
    innings_data: InningsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new innings for a match."""
    # Validate match exists
    match = await match_service.get_by_public_id(db, innings_data.match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{innings_data.match_id}' not found"
        )
    
    # Validate batting team
    batting_team = await team_service.get_by_public_id(db, innings_data.batting_team_id)
    if not batting_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batting team with ID '{innings_data.batting_team_id}' not found"
        )
    
    # Validate bowling team
    bowling_team = await team_service.get_by_public_id(db, innings_data.bowling_team_id)
    if not bowling_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bowling team with ID '{innings_data.bowling_team_id}' not found"
        )
    
    # Check if innings with same match and seq_number already exists
    existing_innings = await innings_service.get_by_match_and_seq(
        db,
        match_id=match.id,
        seq_number=innings_data.seq_number
    )
    if existing_innings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Innings {innings_data.seq_number} already exists for this match"
        )
    
    # Create innings
    innings_dict = innings_data.model_dump()
    innings_dict["match_id"] = match.id
    innings_dict["batting_team_id"] = batting_team.id
    innings_dict["bowling_team_id"] = bowling_team.id
    
    innings = await innings_service.create(db, **innings_dict)
    await db.commit()
    
    # Return with full details
    innings = await innings_service.get_innings_with_details(db, innings.public_id)
    return innings


@router.get(
    "",
    response_model=PaginatedResponse[InningsSummary],
    summary="List all innings"
)
async def list_innings(
    pagination: PaginationParams = Depends(),
    match_id: str = Query(None, description="Filter by match ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of innings."""
    if match_id:
        match = await match_service.get_by_public_id(db, match_id)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID '{match_id}' not found"
            )
        
        innings_list = await innings_service.get_by_match(
            db,
            match_id=match.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(innings_list)
    else:
        innings_list = await innings_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            order_by="id",
            order_desc=True
        )
        total = await innings_service.count(db)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=innings_list
    )


@router.get(
    "/{innings_id}",
    response_model=InningsResponse,
    summary="Get innings by ID"
)
async def get_innings(
    innings_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific innings by public ID with full details."""
    innings = await innings_service.get_innings_with_details(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    # Calculate score
    score = await innings_service.calculate_innings_score(db, innings)
    
    # Add calculated fields to response
    innings_dict = innings.__dict__.copy()
    innings_dict.update(score)
    
    return innings_dict


@router.get(
    "/{innings_id}/score",
    summary="Get innings score"
)
async def get_innings_score(
    innings_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get calculated score for an innings."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    score = await innings_service.calculate_innings_score(db, innings)
    return score


@router.get(
    "/{innings_id}/partnership",
    summary="Get current batting partnership"
)
async def get_current_partnership(
    innings_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get current batting partnership details."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    partnership = await innings_service.get_current_batting_partnership(db, innings)
    return partnership


@router.patch(
    "/{innings_id}",
    response_model=InningsResponse,
    summary="Update innings"
)
async def update_innings(
    innings_id: str,
    innings_data: InningsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an innings' information."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = innings_data.model_dump(exclude_unset=True)
    
    # Validate and convert IDs if provided
    if "batting_team_id" in update_data and update_data["batting_team_id"]:
        batting_team = await team_service.get_by_public_id(db, update_data["batting_team_id"])
        if not batting_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batting team with ID '{update_data['batting_team_id']}' not found"
            )
        update_data["batting_team_id"] = batting_team.id
    
    if "bowling_team_id" in update_data and update_data["bowling_team_id"]:
        bowling_team = await team_service.get_by_public_id(db, update_data["bowling_team_id"])
        if not bowling_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bowling team with ID '{update_data['bowling_team_id']}' not found"
            )
        update_data["bowling_team_id"] = bowling_team.id
    
    innings = await innings_service.update(db, obj=innings, update_data=update_data)
    await db.commit()
    
    # Return with full details
    innings = await innings_service.get_innings_with_details(db, innings.public_id)
    return innings


@router.post(
    "/{innings_id}/close",
    response_model=InningsResponse,
    summary="Close innings"
)
async def close_innings(
    innings_id: str,
    reason: str = Query("NORMAL", description="Reason for closing (NORMAL, DECLARED, FORFEITED)"),
    db: AsyncSession = Depends(get_db)
):
    """Close an innings (declared, all out, etc.)."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    valid_reasons = ["NORMAL", "DECLARED", "FORFEITED"]
    if reason not in valid_reasons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"
        )
    
    innings = await innings_service.close_innings(db, innings, reason)
    await db.commit()
    
    # Return with full details
    innings = await innings_service.get_innings_with_details(db, innings.public_id)
    return innings


@router.delete(
    "/{innings_id}",
    response_model=MessageResponse,
    summary="Delete innings"
)
async def delete_innings(
    innings_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an innings."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    await innings_service.delete(db, obj=innings)
    await db.commit()
    
    return MessageResponse(
        message=f"Innings deleted successfully"
    )

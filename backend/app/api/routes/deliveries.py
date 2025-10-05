"""Delivery API endpoints - Ball-by-ball scoring."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.delivery_service import delivery_service
from app.services.innings_service import innings_service
from app.services.player_service import player_service
from app.schemas.delivery import (
    DeliveryCreate, DeliveryUpdate, DeliveryResponse, DeliverySummary,
    BallByBallRequest
)
from app.schemas import PaginatedResponse, MessageResponse, PaginationParams

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post(
    "",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a delivery"
)
async def record_delivery(
    delivery_data: DeliveryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Record a new delivery (ball) in an innings."""
    # Validate innings exists
    innings = await innings_service.get_by_public_id(db, delivery_data.innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{delivery_data.innings_id}' not found"
        )
    
    # Validate striker
    striker = await player_service.get_by_public_id(db, delivery_data.striker_id)
    if not striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Striker with ID '{delivery_data.striker_id}' not found"
        )
    
    # Validate non-striker
    non_striker = await player_service.get_by_public_id(db, delivery_data.non_striker_id)
    if not non_striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Non-striker with ID '{delivery_data.non_striker_id}' not found"
        )
    
    # Validate bowler
    bowler = await player_service.get_by_public_id(db, delivery_data.bowler_id)
    if not bowler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bowler with ID '{delivery_data.bowler_id}' not found"
        )
    
    # Validate out player if wicket
    out_player_id = None
    if delivery_data.out_player_id:
        out_player = await player_service.get_by_public_id(db, delivery_data.out_player_id)
        if not out_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Out player with ID '{delivery_data.out_player_id}' not found"
            )
        out_player_id = out_player.id
    
    # Validate fielder if provided
    fielder_id = None
    if delivery_data.fielder_id:
        fielder = await player_service.get_by_public_id(db, delivery_data.fielder_id)
        if not fielder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fielder with ID '{delivery_data.fielder_id}' not found"
            )
        fielder_id = fielder.id
    
    # Prepare delivery data
    delivery_dict = delivery_data.model_dump(exclude={"innings_id", "striker_id", "non_striker_id", "bowler_id", "out_player_id", "fielder_id"})
    delivery_dict["striker_id"] = striker.id
    delivery_dict["non_striker_id"] = non_striker.id
    delivery_dict["bowler_id"] = bowler.id
    delivery_dict["out_player_id"] = out_player_id
    delivery_dict["fielder_id"] = fielder_id
    
    # Record delivery
    delivery = await delivery_service.record_delivery(db, innings.id, delivery_dict)
    await db.commit()
    
    # Return with full details
    delivery = await delivery_service.get_delivery_with_details(db, delivery.public_id)
    return delivery


@router.post(
    "/ball-by-ball",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record ball-by-ball delivery (live scoring)"
)
async def record_ball_by_ball(
    innings_id: str,
    ball_data: BallByBallRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive endpoint for recording a delivery in live scoring.
    Validates all players and automatically calculates legal delivery status.
    """
    # Validate innings exists
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    # Validate all players
    striker = await player_service.get_by_public_id(db, ball_data.striker_id)
    if not striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Striker with ID '{ball_data.striker_id}' not found"
        )
    
    non_striker = await player_service.get_by_public_id(db, ball_data.non_striker_id)
    if not non_striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Non-striker with ID '{ball_data.non_striker_id}' not found"
        )
    
    bowler = await player_service.get_by_public_id(db, ball_data.bowler_id)
    if not bowler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bowler with ID '{ball_data.bowler_id}' not found"
        )
    
    # Validate out player if wicket
    out_player_id = None
    if ball_data.out_player_id:
        out_player = await player_service.get_by_public_id(db, ball_data.out_player_id)
        if not out_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Out player with ID '{ball_data.out_player_id}' not found"
            )
        out_player_id = out_player.id
    
    # Validate fielder if provided
    fielder_id = None
    if ball_data.fielder_id:
        fielder = await player_service.get_by_public_id(db, ball_data.fielder_id)
        if not fielder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fielder with ID '{ball_data.fielder_id}' not found"
            )
        fielder_id = fielder.id
    
    # Prepare delivery data
    delivery_dict = ball_data.model_dump()
    delivery_dict["striker_id"] = striker.id
    delivery_dict["non_striker_id"] = non_striker.id
    delivery_dict["bowler_id"] = bowler.id
    delivery_dict["out_player_id"] = out_player_id
    delivery_dict["fielder_id"] = fielder_id
    
    # Record delivery
    delivery = await delivery_service.record_delivery(db, innings.id, delivery_dict)
    await db.commit()
    
    # Return with full details
    delivery = await delivery_service.get_delivery_with_details(db, delivery.public_id)
    return delivery


@router.get(
    "",
    response_model=PaginatedResponse[DeliverySummary],
    summary="List all deliveries"
)
async def list_deliveries(
    pagination: PaginationParams = Depends(),
    innings_id: str = Query(None, description="Filter by innings ID"),
    over_number: int = Query(None, ge=1, description="Filter by over number"),
    db: AsyncSession = Depends(get_db)
):
    """Get a paginated list of deliveries."""
    if innings_id and over_number:
        innings = await innings_service.get_by_public_id(db, innings_id)
        if not innings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Innings with ID '{innings_id}' not found"
            )
        
        deliveries = await delivery_service.get_deliveries_in_over(
            db,
            innings_id=innings.id,
            over_number=over_number
        )
        total = len(deliveries)
    elif innings_id:
        innings = await innings_service.get_by_public_id(db, innings_id)
        if not innings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Innings with ID '{innings_id}' not found"
            )
        
        deliveries = await delivery_service.get_by_innings(
            db,
            innings_id=innings.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        total = len(deliveries)
    else:
        deliveries = await delivery_service.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            order_by="id",
            order_desc=True
        )
        total = await delivery_service.count(db)
    
    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=deliveries
    )


@router.get(
    "/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Get delivery by ID"
)
async def get_delivery(
    delivery_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific delivery by public ID with full details."""
    delivery = await delivery_service.get_delivery_with_details(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID '{delivery_id}' not found"
        )
    return delivery


@router.get(
    "/innings/{innings_id}/over/{over_number}",
    summary="Get over summary"
)
async def get_over_summary(
    innings_id: str,
    over_number: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get summary of a specific over."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    summary = await delivery_service.get_over_summary(db, innings.id, over_number)
    return summary


@router.get(
    "/innings/{innings_id}/batsman/{player_id}/stats",
    summary="Get batsman statistics"
)
async def get_batsman_stats(
    innings_id: str,
    player_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get batting statistics for a player in an innings."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    
    stats = await delivery_service.get_batsman_stats(db, innings.id, player.id)
    return stats


@router.get(
    "/innings/{innings_id}/bowler/{player_id}/stats",
    summary="Get bowler statistics"
)
async def get_bowler_stats(
    innings_id: str,
    player_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get bowling statistics for a player in an innings."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    
    stats = await delivery_service.get_bowler_stats(db, innings.id, player.id)
    return stats


@router.get(
    "/innings/{innings_id}/wagon-wheel",
    summary="Get wagon wheel data"
)
async def get_wagon_wheel(
    innings_id: str,
    player_id: str = Query(None, description="Filter by player ID"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get wagon wheel shot data for visualization."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    player_internal_id = None
    if player_id:
        player = await player_service.get_by_public_id(db, player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID '{player_id}' not found"
            )
        player_internal_id = player.id
    
    wagon_data = await delivery_service.get_wagon_wheel_data(db, innings.id, player_internal_id)
    return wagon_data


@router.get(
    "/innings/{innings_id}/pitch-map",
    summary="Get pitch map data"
)
async def get_pitch_map(
    innings_id: str,
    bowler_id: str = Query(None, description="Filter by bowler ID"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get pitch map data for ball landing visualization."""
    innings = await innings_service.get_by_public_id(db, innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{innings_id}' not found"
        )
    
    bowler_internal_id = None
    if bowler_id:
        bowler = await player_service.get_by_public_id(db, bowler_id)
        if not bowler:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bowler with ID '{bowler_id}' not found"
            )
        bowler_internal_id = bowler.id
    
    pitch_data = await delivery_service.get_pitch_map_data(db, innings.id, bowler_internal_id)
    return pitch_data


@router.patch(
    "/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Update delivery"
)
async def update_delivery(
    delivery_id: str,
    delivery_data: DeliveryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a delivery's information."""
    delivery = await delivery_service.get_by_public_id(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID '{delivery_id}' not found"
        )
    
    # Only update fields that were provided
    update_data = delivery_data.model_dump(exclude_unset=True)
    
    # Validate and convert player IDs if provided
    if "striker_id" in update_data and update_data["striker_id"]:
        striker = await player_service.get_by_public_id(db, update_data["striker_id"])
        if not striker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Striker with ID '{update_data['striker_id']}' not found"
            )
        update_data["striker_id"] = striker.id
    
    if "non_striker_id" in update_data and update_data["non_striker_id"]:
        non_striker = await player_service.get_by_public_id(db, update_data["non_striker_id"])
        if not non_striker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Non-striker with ID '{update_data['non_striker_id']}' not found"
            )
        update_data["non_striker_id"] = non_striker.id
    
    if "bowler_id" in update_data and update_data["bowler_id"]:
        bowler = await player_service.get_by_public_id(db, update_data["bowler_id"])
        if not bowler:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bowler with ID '{update_data['bowler_id']}' not found"
            )
        update_data["bowler_id"] = bowler.id
    
    if "out_player_id" in update_data and update_data["out_player_id"]:
        out_player = await player_service.get_by_public_id(db, update_data["out_player_id"])
        if not out_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Out player with ID '{update_data['out_player_id']}' not found"
            )
        update_data["out_player_id"] = out_player.id
    
    if "fielder_id" in update_data and update_data["fielder_id"]:
        fielder = await player_service.get_by_public_id(db, update_data["fielder_id"])
        if not fielder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fielder with ID '{update_data['fielder_id']}' not found"
            )
        update_data["fielder_id"] = fielder.id
    
    delivery = await delivery_service.update(db, obj=delivery, update_data=update_data)
    await db.commit()
    
    # Return with full details
    delivery = await delivery_service.get_delivery_with_details(db, delivery.public_id)
    return delivery


@router.post(
    "/{delivery_id}/correct",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create corrected delivery"
)
async def correct_delivery(
    delivery_id: str,
    corrected_data: DeliveryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a corrected version of a delivery."""
    original_delivery = await delivery_service.get_by_public_id(db, delivery_id)
    if not original_delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Original delivery with ID '{delivery_id}' not found"
        )
    
    # Validate all players (similar to record_delivery)
    innings = await innings_service.get_by_public_id(db, corrected_data.innings_id)
    if not innings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings with ID '{corrected_data.innings_id}' not found"
        )
    
    striker = await player_service.get_by_public_id(db, corrected_data.striker_id)
    if not striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Striker with ID '{corrected_data.striker_id}' not found"
        )
    
    non_striker = await player_service.get_by_public_id(db, corrected_data.non_striker_id)
    if not non_striker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Non-striker with ID '{corrected_data.non_striker_id}' not found"
        )
    
    bowler = await player_service.get_by_public_id(db, corrected_data.bowler_id)
    if not bowler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bowler with ID '{corrected_data.bowler_id}' not found"
        )
    
    # Prepare corrected data
    corrected_dict = corrected_data.model_dump(exclude={"innings_id", "striker_id", "non_striker_id", "bowler_id"})
    corrected_dict["innings_id"] = innings.id
    corrected_dict["striker_id"] = striker.id
    corrected_dict["non_striker_id"] = non_striker.id
    corrected_dict["bowler_id"] = bowler.id
    
    # Create corrected delivery
    corrected = await delivery_service.correct_delivery(db, original_delivery.id, corrected_dict)
    await db.commit()
    
    # Return with full details
    corrected = await delivery_service.get_delivery_with_details(db, corrected.public_id)
    return corrected


@router.delete(
    "/{delivery_id}",
    response_model=MessageResponse,
    summary="Delete delivery"
)
async def delete_delivery(
    delivery_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a delivery."""
    delivery = await delivery_service.get_by_public_id(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery with ID '{delivery_id}' not found"
        )
    
    await delivery_service.delete(db, obj=delivery)
    await db.commit()
    
    return MessageResponse(
        message=f"Delivery deleted successfully"
    )

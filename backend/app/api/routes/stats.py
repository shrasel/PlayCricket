"""Statistics and analytics endpoints."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.services.match_service import match_service
from app.services.innings_service import innings_service
from app.services.delivery_service import delivery_service
from app.services.player_service import player_service
from app.models.delivery import Delivery

router = APIRouter(prefix="/stats", tags=["Statistics & Analytics"])


@router.get(
    "/matches/{match_id}/scorecard",
    summary="Get match scorecard"
)
async def get_match_scorecard(
    match_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive scorecard for a match."""
    # Get match with full details
    match = await match_service.get_match_with_full_details(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    # Get all innings for the match
    innings_list = await innings_service.get_by_match(db, match.id)
    
    scorecard_innings = []
    for innings in innings_list:
        # Calculate innings score
        score = await innings_service.calculate_innings_score(db, innings)
        
        # Get batting scorecard (player-wise stats)
        batting_query = select(
            Delivery.striker_id,
            func.sum(Delivery.runs_batter).label("runs"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("balls_faced"),
            func.count(Delivery.id).filter(Delivery.is_four == True).label("fours"),
            func.count(Delivery.id).filter(Delivery.is_six == True).label("sixes")
        ).where(
            Delivery.innings_id == innings.id
        ).group_by(Delivery.striker_id)
        
        batting_result = await db.execute(batting_query)
        batting_stats = []
        for row in batting_result:
            player = await player_service.get_by_id(db, row.striker_id, load_relationships=[])
            strike_rate = round((row.runs / row.balls_faced * 100), 2) if row.balls_faced > 0 else 0.0
            
            # Check if player got out
            wicket_query = select(Delivery).where(
                Delivery.innings_id == innings.id,
                Delivery.out_player_id == row.striker_id,
                Delivery.wicket_type.isnot(None)
            ).limit(1)
            wicket_result = await db.execute(wicket_query)
            wicket = wicket_result.scalar_one_or_none()
            
            batting_stats.append({
                "player_id": player.public_id,
                "player_name": player.full_name,
                "runs": row.runs or 0,
                "balls_faced": row.balls_faced or 0,
                "fours": row.fours or 0,
                "sixes": row.sixes or 0,
                "strike_rate": strike_rate,
                "is_out": wicket is not None,
                "wicket_type": wicket.wicket_type if wicket else None
            })
        
        # Get bowling scorecard (bowler-wise stats)
        bowling_query = select(
            Delivery.bowler_id,
            func.sum(Delivery.runs_batter + Delivery.runs_extras).label("runs_conceded"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("legal_balls"),
            func.count(Delivery.id).filter(Delivery.wicket_type.isnot(None)).label("wickets"),
            func.count(Delivery.id).filter(Delivery.extra_type == "WIDE").label("wides"),
            func.count(Delivery.id).filter(Delivery.extra_type == "NO_BALL").label("no_balls")
        ).where(
            Delivery.innings_id == innings.id
        ).group_by(Delivery.bowler_id)
        
        bowling_result = await db.execute(bowling_query)
        bowling_stats = []
        for row in bowling_result:
            player = await player_service.get_by_id(db, row.bowler_id, load_relationships=[])
            
            # Calculate overs
            complete_overs = row.legal_balls // 6
            balls_in_current_over = row.legal_balls % 6
            overs = float(f"{complete_overs}.{balls_in_current_over}")
            
            # Calculate economy rate
            economy_rate = round((row.runs_conceded / overs), 2) if overs > 0 else 0.0
            
            bowling_stats.append({
                "player_id": player.public_id,
                "player_name": player.full_name,
                "overs": overs,
                "runs_conceded": row.runs_conceded or 0,
                "wickets": row.wickets or 0,
                "economy_rate": economy_rate,
                "wides": row.wides or 0,
                "no_balls": row.no_balls or 0
            })
        
        scorecard_innings.append({
            "innings_id": innings.public_id,
            "innings_number": innings.seq_number,
            "batting_team_id": innings.batting_team.public_id,
            "batting_team_name": innings.batting_team.name,
            "bowling_team_id": innings.bowling_team.public_id,
            "bowling_team_name": innings.bowling_team.name,
            "total_runs": score["total_runs"],
            "total_wickets": score["total_wickets"],
            "total_overs": score["total_overs"],
            "is_all_out": score["is_all_out"],
            "run_rate": score["run_rate"],
            "batting": sorted(batting_stats, key=lambda x: x["runs"], reverse=True),
            "bowling": sorted(bowling_stats, key=lambda x: x["wickets"], reverse=True)
        })
    
    return {
        "match_id": match.public_id,
        "match_type": match.match_type,
        "status": match.status,
        "venue": {
            "id": match.venue.public_id,
            "name": match.venue.name,
            "city": match.venue.city
        } if match.venue else None,
        "innings": scorecard_innings,
        "result": {
            "winning_team_id": match.winning_team.public_id if match.winning_team else None,
            "winning_team_name": match.winning_team.name if match.winning_team else None,
            "result_type": match.result_type,
            "result_margin": match.result_margin
        } if match.status == "COMPLETED" else None
    }


@router.get(
    "/players/{player_id}/career",
    summary="Get player career statistics"
)
async def get_player_career_stats(
    player_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive career statistics for a player."""
    player = await player_service.get_by_public_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID '{player_id}' not found"
        )
    
    # Batting stats across all innings
    batting_query = select(
        func.count(func.distinct(Delivery.innings_id)).label("innings_batted"),
        func.sum(Delivery.runs_batter).label("total_runs"),
        func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("balls_faced"),
        func.count(Delivery.id).filter(Delivery.is_four == True).label("fours"),
        func.count(Delivery.id).filter(Delivery.is_six == True).label("sixes"),
        func.count(Delivery.id).filter(
            Delivery.wicket_type.isnot(None) & (Delivery.out_player_id == player.id)
        ).label("dismissals")
    ).where(Delivery.striker_id == player.id)
    
    batting_result = await db.execute(batting_query)
    batting_row = batting_result.one()
    
    # Bowling stats across all innings
    bowling_query = select(
        func.count(func.distinct(Delivery.innings_id)).label("innings_bowled"),
        func.sum(Delivery.runs_batter + Delivery.runs_extras).label("runs_conceded"),
        func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("legal_balls"),
        func.count(Delivery.id).filter(Delivery.wicket_type.isnot(None)).label("wickets")
    ).where(Delivery.bowler_id == player.id)
    
    bowling_result = await db.execute(bowling_query)
    bowling_row = bowling_result.one()
    
    # Calculate batting averages
    total_runs = batting_row.total_runs or 0
    balls_faced = batting_row.balls_faced or 0
    dismissals = batting_row.dismissals or 0
    
    batting_average = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
    strike_rate = round((total_runs / balls_faced * 100), 2) if balls_faced > 0 else 0.0
    
    # Calculate bowling averages
    runs_conceded = bowling_row.runs_conceded or 0
    wickets = bowling_row.wickets or 0
    legal_balls = bowling_row.legal_balls or 0
    
    complete_overs = legal_balls // 6
    balls_in_over = legal_balls % 6
    overs_bowled = float(f"{complete_overs}.{balls_in_over}")
    
    bowling_average = round(runs_conceded / wickets, 2) if wickets > 0 else 0.0
    economy_rate = round((runs_conceded / overs_bowled), 2) if overs_bowled > 0 else 0.0
    
    return {
        "player": {
            "id": player.public_id,
            "full_name": player.full_name,
            "known_as": player.known_as,
            "batting_style": player.batting_style,
            "bowling_style": player.bowling_style
        },
        "batting": {
            "innings": batting_row.innings_batted or 0,
            "runs": total_runs,
            "balls_faced": balls_faced,
            "average": batting_average,
            "strike_rate": strike_rate,
            "fours": batting_row.fours or 0,
            "sixes": batting_row.sixes or 0,
            "dismissals": dismissals,
            "not_outs": (batting_row.innings_batted or 0) - dismissals
        },
        "bowling": {
            "innings": bowling_row.innings_bowled or 0,
            "overs": overs_bowled,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "average": bowling_average,
            "economy_rate": economy_rate
        }
    }


@router.get(
    "/matches/{match_id}/summary",
    summary="Get match summary"
)
async def get_match_summary(
    match_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get quick match summary with current scores."""
    match = await match_service.get_match_with_full_details(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found"
        )
    
    # Get all innings
    innings_list = await innings_service.get_by_match(db, match.id)
    
    innings_summary = []
    for innings in innings_list:
        score = await innings_service.calculate_innings_score(db, innings)
        innings_summary.append({
            "innings_number": innings.seq_number,
            "batting_team": innings.batting_team.short_name or innings.batting_team.name,
            "score": f"{score['total_runs']}/{score['total_wickets']}" if not score['is_all_out'] else f"{score['total_runs']}",
            "overs": score['total_overs'],
            "run_rate": score['run_rate']
        })
    
    return {
        "match_id": match.public_id,
        "match_type": match.match_type,
        "status": match.status,
        "venue": match.venue.name if match.venue else None,
        "innings": innings_summary,
        "result": match.result_margin if match.status == "COMPLETED" else None
    }

"""Delivery service for ball-by-ball scoring."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.delivery import Delivery
from app.models.innings import Innings
from app.services.base_service import BaseService


class DeliveryService(BaseService[Delivery]):
    """Service for Delivery operations (ball-by-ball scoring)."""
    
    def __init__(self):
        """Initialize DeliveryService."""
        super().__init__(Delivery)
    
    async def get_by_innings(
        self,
        db: AsyncSession,
        innings_id: int,
        *,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Delivery]:
        """Get deliveries by innings."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"innings_id": innings_id},
            order_by="over_number"
        )
    
    async def get_deliveries_in_over(
        self,
        db: AsyncSession,
        innings_id: int,
        over_number: int
    ) -> List[Delivery]:
        """Get all deliveries in a specific over."""
        query = select(Delivery).where(
            and_(
                Delivery.innings_id == innings_id,
                Delivery.over_number == over_number
            )
        ).order_by(Delivery.ball_in_over)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_delivery_with_details(
        self,
        db: AsyncSession,
        public_id: str
    ) -> Optional[Delivery]:
        """Get delivery with all relationships loaded."""
        query = select(Delivery).where(Delivery.public_id == public_id).options(
            selectinload(Delivery.innings),
            selectinload(Delivery.striker),
            selectinload(Delivery.non_striker),
            selectinload(Delivery.bowler),
            selectinload(Delivery.out_player),
            selectinload(Delivery.fielder)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def record_delivery(
        self,
        db: AsyncSession,
        innings_id: int,
        delivery_data: Dict[str, Any]
    ) -> Delivery:
        """Record a new delivery with automatic calculations."""
        # Determine if it's a legal delivery
        extra_type = delivery_data.get("extra_type")
        is_legal_delivery = extra_type not in ["WIDE", "NO_BALL"] if extra_type else True
        
        # Set timestamp if not provided
        if "ts_utc" not in delivery_data or delivery_data["ts_utc"] is None:
            delivery_data["ts_utc"] = datetime.utcnow()
        
        # Create delivery
        delivery = await self.create(
            db,
            innings_id=innings_id,
            is_legal_delivery=is_legal_delivery,
            **delivery_data
        )
        
        return delivery
    
    async def correct_delivery(
        self,
        db: AsyncSession,
        original_delivery_id: int,
        corrected_data: Dict[str, Any]
    ) -> Delivery:
        """Create a corrected version of a delivery."""
        corrected_data["replaces_delivery_id"] = original_delivery_id
        corrected_data["ts_utc"] = datetime.utcnow()
        
        delivery = await self.create(db, **corrected_data)
        return delivery
    
    async def get_batsman_stats(
        self,
        db: AsyncSession,
        innings_id: int,
        player_id: int
    ) -> Dict[str, Any]:
        """Get batting statistics for a player in an innings."""
        query = select(
            func.sum(Delivery.runs_batter).label("runs"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("balls_faced"),
            func.count(Delivery.id).filter(Delivery.is_four == True).label("fours"),
            func.count(Delivery.id).filter(Delivery.is_six == True).label("sixes"),
            func.count(Delivery.id).filter(
                and_(
                    Delivery.wicket_type.isnot(None),
                    Delivery.out_player_id == player_id
                )
            ).label("dismissals")
        ).where(
            and_(
                Delivery.innings_id == innings_id,
                Delivery.striker_id == player_id
            )
        )
        
        result = await db.execute(query)
        row = result.one()
        
        runs = row.runs or 0
        balls_faced = row.balls_faced or 0
        fours = row.fours or 0
        sixes = row.sixes or 0
        dismissals = row.dismissals or 0
        
        strike_rate = round((runs / balls_faced * 100), 2) if balls_faced > 0 else 0.0
        
        return {
            "runs": runs,
            "balls_faced": balls_faced,
            "fours": fours,
            "sixes": sixes,
            "strike_rate": strike_rate,
            "is_out": dismissals > 0,
            "is_not_out": dismissals == 0 and balls_faced > 0
        }
    
    async def get_bowler_stats(
        self,
        db: AsyncSession,
        innings_id: int,
        player_id: int
    ) -> Dict[str, Any]:
        """Get bowling statistics for a player in an innings."""
        query = select(
            func.sum(Delivery.runs_batter + Delivery.runs_extras).label("runs_conceded"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("legal_balls"),
            func.count(Delivery.id).filter(Delivery.wicket_type.isnot(None)).label("wickets"),
            func.count(Delivery.id).filter(Delivery.extra_type == "WIDE").label("wides"),
            func.count(Delivery.id).filter(Delivery.extra_type == "NO_BALL").label("no_balls"),
            func.count(Delivery.id).filter(Delivery.is_four == True).label("fours_conceded"),
            func.count(Delivery.id).filter(Delivery.is_six == True).label("sixes_conceded")
        ).where(
            and_(
                Delivery.innings_id == innings_id,
                Delivery.bowler_id == player_id
            )
        )
        
        result = await db.execute(query)
        row = result.one()
        
        runs_conceded = row.runs_conceded or 0
        legal_balls = row.legal_balls or 0
        wickets = row.wickets or 0
        wides = row.wides or 0
        no_balls = row.no_balls or 0
        
        # Calculate overs
        complete_overs = legal_balls // 6
        balls_in_current_over = legal_balls % 6
        overs = float(f"{complete_overs}.{balls_in_current_over}")
        
        # Calculate economy rate
        economy_rate = round((runs_conceded / overs), 2) if overs > 0 else 0.0
        
        return {
            "overs": overs,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "economy_rate": economy_rate,
            "wides": wides,
            "no_balls": no_balls,
            "fours_conceded": row.fours_conceded or 0,
            "sixes_conceded": row.sixes_conceded or 0
        }
    
    async def get_over_summary(
        self,
        db: AsyncSession,
        innings_id: int,
        over_number: int
    ) -> Dict[str, Any]:
        """Get summary of an over."""
        deliveries = await self.get_deliveries_in_over(db, innings_id, over_number)
        
        total_runs = sum(d.runs_batter + d.runs_extras for d in deliveries)
        wickets = sum(1 for d in deliveries if d.wicket_type is not None)
        legal_balls = sum(1 for d in deliveries if d.is_legal_delivery)
        extras = sum(d.runs_extras for d in deliveries)
        
        return {
            "over_number": over_number,
            "total_runs": total_runs,
            "wickets": wickets,
            "legal_balls": legal_balls,
            "extras": extras,
            "deliveries": deliveries
        }
    
    async def get_wagon_wheel_data(
        self,
        db: AsyncSession,
        innings_id: int,
        player_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get wagon wheel shot data for visualization."""
        query = select(Delivery).where(
            and_(
                Delivery.innings_id == innings_id,
                Delivery.wagon_x.isnot(None),
                Delivery.wagon_y.isnot(None)
            )
        )
        
        if player_id:
            query = query.where(Delivery.striker_id == player_id)
        
        result = await db.execute(query)
        deliveries = result.scalars().all()
        
        wagon_data = []
        for d in deliveries:
            wagon_data.append({
                "x": d.wagon_x,
                "y": d.wagon_y,
                "runs": d.runs_batter,
                "is_four": d.is_four,
                "is_six": d.is_six
            })
        
        return wagon_data
    
    async def get_pitch_map_data(
        self,
        db: AsyncSession,
        innings_id: int,
        bowler_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get pitch map data for ball landing visualization."""
        query = select(Delivery).where(
            and_(
                Delivery.innings_id == innings_id,
                Delivery.pitch_x.isnot(None),
                Delivery.pitch_y.isnot(None)
            )
        )
        
        if bowler_id:
            query = query.where(Delivery.bowler_id == bowler_id)
        
        result = await db.execute(query)
        deliveries = result.scalars().all()
        
        pitch_data = []
        for d in deliveries:
            pitch_data.append({
                "x": d.pitch_x,
                "y": d.pitch_y,
                "runs_conceded": d.runs_batter + d.runs_extras,
                "wicket": d.wicket_type is not None,
                "wicket_type": d.wicket_type
            })
        
        return pitch_data


# Singleton instance
delivery_service = DeliveryService()

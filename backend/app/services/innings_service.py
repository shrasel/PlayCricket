"""Innings service for business logic."""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.innings import Innings
from app.models.delivery import Delivery
from app.services.base_service import BaseService


class InningsService(BaseService[Innings]):
    """Service for Innings operations."""
    
    def __init__(self):
        """Initialize InningsService."""
        super().__init__(Innings)
    
    async def get_by_match(
        self,
        db: AsyncSession,
        match_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Innings]:
        """Get innings by match."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"match_id": match_id},
            order_by="seq_number"
        )
    
    async def get_innings_with_details(
        self,
        db: AsyncSession,
        public_id: str
    ) -> Optional[Innings]:
        """Get innings with all relationships loaded."""
        query = select(Innings).where(Innings.public_id == public_id).options(
            selectinload(Innings.match),
            selectinload(Innings.batting_team),
            selectinload(Innings.bowling_team),
            selectinload(Innings.deliveries)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_match_and_seq(
        self,
        db: AsyncSession,
        match_id: int,
        seq_number: int
    ) -> Optional[Innings]:
        """Get specific innings by match and sequence number."""
        query = select(Innings).where(
            Innings.match_id == match_id,
            Innings.seq_number == seq_number
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_innings_score(
        self,
        db: AsyncSession,
        innings: Innings
    ) -> Dict[str, Any]:
        """Calculate innings score from deliveries."""
        query = select(
            func.sum(Delivery.runs_batter + Delivery.runs_extras).label("total_runs"),
            func.count(Delivery.id).filter(Delivery.wicket_type.isnot(None)).label("total_wickets"),
            func.max(Delivery.over_number).label("max_over"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("legal_balls")
        ).where(Delivery.innings_id == innings.id)
        
        result = await db.execute(query)
        row = result.one()
        
        total_runs = row.total_runs or 0
        total_wickets = row.total_wickets or 0
        max_over = row.max_over or 0
        legal_balls = row.legal_balls or 0
        
        # Calculate overs (complete overs + balls in current over)
        complete_overs = max_over - 1 if max_over > 0 else 0
        balls_in_current_over = legal_balls % 6 if legal_balls > 0 else 0
        total_overs = float(f"{complete_overs}.{balls_in_current_over}")
        
        # Check if all out (10 wickets for standard cricket)
        is_all_out = total_wickets >= 10
        
        return {
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "total_overs": total_overs,
            "is_all_out": is_all_out,
            "run_rate": round(total_runs / total_overs, 2) if total_overs > 0 else 0.0
        }
    
    async def get_current_batting_partnership(
        self,
        db: AsyncSession,
        innings: Innings
    ) -> Dict[str, Any]:
        """Get current batting partnership details."""
        # Get the last delivery to find current batsmen
        query = select(Delivery).where(
            Delivery.innings_id == innings.id
        ).order_by(Delivery.over_number.desc(), Delivery.ball_in_over.desc()).limit(1)
        
        result = await db.execute(query)
        last_delivery = result.scalar_one_or_none()
        
        if not last_delivery:
            return {
                "striker_id": None,
                "non_striker_id": None,
                "partnership_runs": 0,
                "partnership_balls": 0
            }
        
        striker_id = last_delivery.striker_id
        non_striker_id = last_delivery.non_striker_id
        
        # Find when this partnership started (last wicket)
        last_wicket_query = select(Delivery).where(
            Delivery.innings_id == innings.id,
            Delivery.wicket_type.isnot(None)
        ).order_by(Delivery.over_number.desc(), Delivery.ball_in_over.desc()).limit(1)
        
        last_wicket_result = await db.execute(last_wicket_query)
        last_wicket = last_wicket_result.scalar_one_or_none()
        
        # Calculate partnership from last wicket onwards
        partnership_query = select(
            func.sum(Delivery.runs_batter + Delivery.runs_extras).label("runs"),
            func.count(Delivery.id).filter(Delivery.is_legal_delivery == True).label("balls")
        ).where(Delivery.innings_id == innings.id)
        
        if last_wicket:
            partnership_query = partnership_query.where(
                Delivery.id > last_wicket.id
            )
        
        partnership_result = await db.execute(partnership_query)
        partnership_row = partnership_result.one()
        
        return {
            "striker_id": striker_id,
            "non_striker_id": non_striker_id,
            "partnership_runs": partnership_row.runs or 0,
            "partnership_balls": partnership_row.balls or 0
        }
    
    async def close_innings(
        self,
        db: AsyncSession,
        innings: Innings,
        reason: str = "NORMAL"
    ) -> Innings:
        """Close innings (declared, all out, etc.)."""
        if reason == "DECLARED":
            innings.declared = True
        elif reason == "FORFEITED":
            innings.forfeited = True
        
        await db.flush()
        await db.refresh(innings)
        return innings


# Singleton instance
innings_service = InningsService()

"""Base service class with common CRUD operations."""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """Base service with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize service with model class."""
        self.model = model
    
    async def get_by_id(
        self,
        db: AsyncSession,
        id: int,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a record by internal ID."""
        query = select(self.model).where(self.model.id == id)
        
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_public_id(
        self,
        db: AsyncSession,
        public_id: str,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a record by public ULID."""
        query = select(self.model).where(self.model.public_id == public_id)
        
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        load_relationships: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        query = select(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if order_desc else order_column)
        else:
            query = query.order_by(self.model.id.desc())
        
        # Apply relationships
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filtering."""
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        result = await db.execute(query)
        return result.scalar_one()
    
    async def create(
        self,
        db: AsyncSession,
        **kwargs
    ) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        obj: ModelType,
        update_data: Dict[str, Any]
    ) -> ModelType:
        """Update a record."""
        for key, value in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        await db.flush()
        await db.refresh(obj)
        return obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        obj: ModelType
    ) -> None:
        """Delete a record."""
        await db.delete(obj)
        await db.flush()
    
    async def search(
        self,
        db: AsyncSession,
        search_term: str,
        search_fields: List[str],
        *,
        skip: int = 0,
        limit: int = 100,
        load_relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Search records by term across multiple fields."""
        query = select(self.model)
        
        # Build OR conditions for search
        conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                conditions.append(
                    getattr(self.model, field).ilike(f"%{search_term}%")
                )
        
        if conditions:
            query = query.where(or_(*conditions))
        
        # Apply relationships
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

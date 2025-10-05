"""Base model for all database models."""
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Primary key (internal use only, not exposed via API)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

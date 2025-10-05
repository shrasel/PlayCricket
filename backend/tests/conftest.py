"""
Test fixtures and configuration for pytest
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.models.base import Base
from app.core.cache import RedisCache
from app.main import app


# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://cricket_user:cricket_pass_dev@localhost:5432/playcricket_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test
    """
    # Create test engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def redis_cache() -> AsyncGenerator[RedisCache, None]:
    """
    Create Redis cache for tests
    """
    cache = RedisCache()
    await cache.connect()
    
    yield cache
    
    # Clear all test keys
    await cache.invalidate_pattern("test:*")
    await cache.close()


@pytest.fixture
def client():
    """
    FastAPI test client
    """
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def sample_team_data():
    """Sample team data for tests"""
    return {
        "name": "Mumbai Indians",
        "short_name": "MI",
        "country_code": "IND",
        "primary_color": "#004BA0",
        "secondary_color": "#D1AB3E",
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for tests"""
    return {
        "full_name": "Rohit Gurunath Sharma",
        "known_as": "Rohit Sharma",
        "date_of_birth": "1987-04-30",
        "batting_style": "RHB",
        "bowling_style": None,
        "nationality": "IND",
    }


@pytest.fixture
def sample_venue_data():
    """Sample venue data for tests"""
    return {
        "name": "Wankhede Stadium",
        "city": "Mumbai",
        "country_code": "IND",
        "timezone_name": "Asia/Kolkata",
        "capacity": 33000,
    }
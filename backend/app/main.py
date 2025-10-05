"""
PlayCricket API - FastAPI Application
High-performance cricket platform with real-time live scoring
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.core.cache import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting PlayCricket API...")
    
    # Initialize database tables (development only)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Test Redis connection
    await redis_client.ping()
    print("✅ Redis connection established")
    
    print(f"📊 API Documentation: {settings.DOCS_URL}")
    print(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down PlayCricket API...")
    await redis_client.close()
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Cricinfo-class cricket platform with live scoring and analytics",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    default_response_class=ORJSONResponse,  # Faster JSON serialization
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "🏏 PlayCricket API",
        "version": settings.APP_VERSION,
        "docs": settings.DOCS_URL,
    }


# Import and include routers
from app.api.routes import (
    teams,
    players,
    venues,
    tournaments,
    matches,
    innings,
    deliveries,
    stats,
    auth,
    users,
    roles
)

# Register API routers
# Authentication routes (public access)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(roles.router, prefix=settings.API_V1_PREFIX)
app.include_router(roles.audit_router, prefix=settings.API_V1_PREFIX)

# Cricket data routes
app.include_router(teams.router, prefix=settings.API_V1_PREFIX)
app.include_router(players.router, prefix=settings.API_V1_PREFIX)
app.include_router(venues.router, prefix=settings.API_V1_PREFIX)
app.include_router(tournaments.router, prefix=settings.API_V1_PREFIX)
app.include_router(matches.router, prefix=settings.API_V1_PREFIX)
app.include_router(innings.router, prefix=settings.API_V1_PREFIX)
app.include_router(deliveries.router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
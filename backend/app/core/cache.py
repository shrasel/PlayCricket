"""
Redis Cache Configuration
Async Redis client for caching and session management
"""

from typing import Any, Optional
import json
from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings


class RedisCache:
    """Async Redis cache wrapper"""
    
    def __init__(self):
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
        self.client: Optional[Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self.client:
            self.client = Redis(connection_pool=self.pool)
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            await self.pool.disconnect()
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        if not self.client:
            await self.connect()
        return await self.client.ping()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            await self.connect()
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self.client:
            await self.connect()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if ttl:
            return await self.client.setex(key, ttl, value)
        return await self.client.set(key, value)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            await self.connect()
        return await self.client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            await self.connect()
        return await self.client.exists(key) > 0
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.client:
            await self.connect()
        keys = await self.client.keys(pattern)
        if keys:
            return await self.client.delete(*keys)
        return 0


# Global Redis client instance
redis_client = RedisCache()
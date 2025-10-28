"""
Redis connection and utilities.
Used for sessions, caching, and rate limiting.
"""
from typing import Optional, Any
import json
from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class RedisManager:
    """Redis connection manager with multiple database support."""

    def __init__(self) -> None:
        """Initialize Redis manager."""
        self.main_pool: Optional[ConnectionPool] = None
        self.session_pool: Optional[ConnectionPool] = None
        self.cache_pool: Optional[ConnectionPool] = None
        self.main_client: Optional[Redis] = None
        self.session_client: Optional[Redis] = None
        self.cache_client: Optional[Redis] = None

    async def connect(self) -> None:
        """Connect to Redis and create connection pools."""
        if self.main_client is not None:
            logger.warning("Redis already connected")
            return

        logger.info(f"Connecting to Redis: {settings.redis_url}")

        try:
            # Parse Redis URL
            base_url = settings.redis_url.rsplit('/', 1)[0]

            # Main Redis connection (default DB)
            self.main_pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            self.main_client = Redis(connection_pool=self.main_pool)

            # Session Redis connection
            self.session_pool = ConnectionPool.from_url(
                f"{base_url}/{settings.redis_session_db}",
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            self.session_client = Redis(connection_pool=self.session_pool)

            # Cache Redis connection
            self.cache_pool = ConnectionPool.from_url(
                f"{base_url}/{settings.redis_cache_db}",
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            self.cache_client = Redis(connection_pool=self.cache_pool)

            # Test connections
            await self.main_client.ping()
            await self.session_client.ping()
            await self.cache_client.ping()

            logger.info("Redis connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connections."""
        logger.info("Closing Redis connections")

        if self.main_client:
            await self.main_client.close()
            await self.main_pool.disconnect()

        if self.session_client:
            await self.session_client.close()
            await self.session_pool.disconnect()

        if self.cache_client:
            await self.cache_client.close()
            await self.cache_pool.disconnect()

        self.main_client = None
        self.session_client = None
        self.cache_client = None

        logger.info("Redis connections closed")

    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.

        Returns:
            bool: True if connection is healthy
        """
        if self.main_client is None:
            return False

        try:
            await self.main_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    def get_client(self, db_type: str = "main") -> Redis:
        """
        Get Redis client for specific database.

        Args:
            db_type: Database type (main, session, cache)

        Returns:
            Redis: Redis client

        Raises:
            RuntimeError: If not connected
            ValueError: If db_type is invalid
        """
        if db_type == "main":
            if self.main_client is None:
                raise RuntimeError("Redis not connected. Call connect() first.")
            return self.main_client
        elif db_type == "session":
            if self.session_client is None:
                raise RuntimeError("Redis not connected. Call connect() first.")
            return self.session_client
        elif db_type == "cache":
            if self.cache_client is None:
                raise RuntimeError("Redis not connected. Call connect() first.")
            return self.cache_client
        else:
            raise ValueError(f"Invalid db_type: {db_type}. Must be 'main', 'session', or 'cache'")

    async def set_json(self, key: str, value: Any, expire: Optional[int] = None, db_type: str = "main") -> None:
        """
        Set a JSON value in Redis.

        Args:
            key: Redis key
            value: Value to store (will be JSON encoded)
            expire: Optional expiration time in seconds
            db_type: Database type (main, session, cache)
        """
        client = self.get_client(db_type)
        json_value = json.dumps(value)
        if expire:
            await client.setex(key, expire, json_value)
        else:
            await client.set(key, json_value)

    async def get_json(self, key: str, db_type: str = "main") -> Optional[Any]:
        """
        Get a JSON value from Redis.

        Args:
            key: Redis key
            db_type: Database type (main, session, cache)

        Returns:
            Decoded JSON value or None
        """
        client = self.get_client(db_type)
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None

    async def delete(self, key: str, db_type: str = "main") -> None:
        """
        Delete a key from Redis.

        Args:
            key: Redis key
            db_type: Database type (main, session, cache)
        """
        client = self.get_client(db_type)
        await client.delete(key)

    async def exists(self, key: str, db_type: str = "main") -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key: Redis key
            db_type: Database type (main, session, cache)

        Returns:
            bool: True if key exists
        """
        client = self.get_client(db_type)
        return await client.exists(key) > 0


# Global Redis instance
redis_manager = RedisManager()


async def get_redis(db_type: str = "main") -> Redis:
    """
    Dependency function to get Redis client.
    Use this as a FastAPI dependency.

    Args:
        db_type: Database type (main, session, cache)

    Returns:
        Redis: Redis client
    """
    return redis_manager.get_client(db_type)


__all__ = [
    "redis_manager",
    "get_redis",
]

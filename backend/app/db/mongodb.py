"""
MongoDB connection and utilities.
Uses Motor for async MongoDB operations.
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager."""

    def __init__(self) -> None:
        """Initialize MongoDB manager."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Connect to MongoDB."""
        if self.client is not None:
            logger.warning("MongoDB already connected")
            return

        logger.info(f"Connecting to MongoDB: {settings.mongo_db_name}")

        try:
            self.client = AsyncIOMotorClient(
                settings.mongo_uri,
                minPoolSize=settings.mongo_min_pool_size,
                maxPoolSize=settings.mongo_max_pool_size,
                serverSelectionTimeoutMS=5000,
            )

            self.db = self.client[settings.mongo_db_name]

            # Test connection
            await self.client.admin.command('ping')

            logger.info("MongoDB connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")

    async def health_check(self) -> bool:
        """
        Check if MongoDB connection is healthy.

        Returns:
            bool: True if connection is healthy
        """
        if self.client is None or self.db is None:
            return False

        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get the MongoDB database instance.

        Returns:
            AsyncIOMotorDatabase: MongoDB database

        Raises:
            RuntimeError: If not connected
        """
        if self.db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db

    def get_collection(self, name: str):
        """
        Get a MongoDB collection.

        Args:
            name: Collection name

        Returns:
            AsyncIOMotorCollection: MongoDB collection
        """
        db = self.get_database()
        return db[name]


# Global MongoDB instance
mongodb = MongoDB()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Dependency function to get MongoDB database.
    Use this as a FastAPI dependency.

    Returns:
        AsyncIOMotorDatabase: MongoDB database
    """
    return mongodb.get_database()


# Collection name constants
class Collections:
    """MongoDB collection names."""
    USER_PREFERENCES = "user_preferences"
    THEMES = "themes"
    APP_SETTINGS = "app_settings"
    DASHBOARDS = "dashboard_layouts"
    WIDGETS = "widgets"
    WIDGET_TYPES = "widget_types"
    TRANSLATIONS = "translations"
    BRANDING = "branding"


__all__ = [
    "mongodb",
    "get_mongodb",
    "Collections",
]

"""
Database adapters module.
Factory pattern for selecting the appropriate database adapter based on configuration.
"""
from typing import Union

from app.core.config import settings
from app.core.logging import get_logger
from app.db.adapters.postgresql import PostgreSQLAdapter
from app.db.adapters.sqlserver import SQLServerAdapter


logger = get_logger(__name__)

# Type alias for database adapters
DatabaseAdapterType = Union[PostgreSQLAdapter, SQLServerAdapter]

# Global database adapter instance
_db_adapter: DatabaseAdapterType | None = None


def get_database_adapter() -> DatabaseAdapterType:
    """
    Factory function to get the appropriate database adapter based on configuration.

    Returns:
        DatabaseAdapterType: Configured database adapter

    Raises:
        ValueError: If DB_TYPE is not supported
    """
    global _db_adapter

    if _db_adapter is not None:
        return _db_adapter

    db_type = settings.db_type.lower()

    if db_type == "postgresql":
        logger.info("Using PostgreSQL database adapter")
        _db_adapter = PostgreSQLAdapter()
    elif db_type == "sqlserver":
        logger.info("Using SQL Server database adapter")
        _db_adapter = SQLServerAdapter()
    else:
        raise ValueError(f"Unsupported database type: {db_type}. Must be 'postgresql' or 'sqlserver'")

    return _db_adapter


async def init_database() -> None:
    """Initialize the database connection."""
    adapter = get_database_adapter()
    await adapter.init()
    logger.info(f"Database initialized: {adapter.db_type}")


async def close_database() -> None:
    """Close the database connection."""
    global _db_adapter
    if _db_adapter is not None:
        await _db_adapter.close()
        _db_adapter = None
        logger.info("Database connection closed")


async def get_db_session():
    """
    Dependency function to get a database session.
    Use this as a FastAPI dependency.

    Yields:
        AsyncSession: Database session
    """
    adapter = get_database_adapter()
    async for session in adapter.get_session():
        yield session


__all__ = [
    "DatabaseAdapterType",
    "get_database_adapter",
    "init_database",
    "close_database",
    "get_db_session",
]

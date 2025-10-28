"""
Abstract database adapter protocol.
Defines the interface that all database adapters must implement.
"""
from typing import Protocol, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine


class DatabaseAdapter(Protocol):
    """
    Protocol defining the interface for database adapters.
    Both PostgreSQL and SQL Server adapters must implement this interface.
    """

    async def init(self) -> None:
        """Initialize the database connection and engine."""
        ...

    async def close(self) -> None:
        """Close database connections and cleanup resources."""
        ...

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session.

        Yields:
            AsyncSession: Database session
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        ...

    async def execute_raw(self, query: str, params: Optional[dict] = None) -> any:
        """
        Execute a raw SQL query.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Query result
        """
        ...

    def get_engine(self) -> AsyncEngine:
        """
        Get the SQLAlchemy engine.

        Returns:
            AsyncEngine: Database engine
        """
        ...

    @property
    def db_type(self) -> str:
        """
        Get the database type.

        Returns:
            str: Database type identifier (postgresql or sqlserver)
        """
        ...

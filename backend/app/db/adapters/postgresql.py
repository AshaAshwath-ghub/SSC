"""
PostgreSQL database adapter implementation.
Uses asyncpg driver with SQLAlchemy.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class PostgreSQLAdapter:
    """PostgreSQL database adapter using asyncpg driver."""

    def __init__(self) -> None:
        """Initialize PostgreSQL adapter."""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._db_type = "postgresql"

    async def init(self) -> None:
        """Initialize the database engine and session factory."""
        if self._engine is not None:
            logger.warning("PostgreSQL engine already initialized")
            return

        database_url = settings.database_url
        logger.info(f"Initializing PostgreSQL connection to {settings.db_host}:{settings.db_port}/{settings.db_name}")

        try:
            self._engine = create_async_engine(
                database_url,
                echo=settings.db_echo,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,  # Recycle connections after 1 hour
            )

            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("PostgreSQL connection initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {e}")
            raise

    async def close(self) -> None:
        """Close database connections and cleanup resources."""
        if self._engine:
            logger.info("Closing PostgreSQL connections")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("PostgreSQL connections closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session.

        Yields:
            AsyncSession: Database session
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call init() first.")

        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Session error: {e}")
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        if self._engine is None:
            return False

        try:
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

    async def execute_raw(self, query: str, params: Optional[dict] = None) -> any:
        """
        Execute a raw SQL query.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Query result
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call init() first.")

        async with self._engine.begin() as conn:
            if params:
                result = await conn.execute(text(query), params)
            else:
                result = await conn.execute(text(query))
            return result

    def get_engine(self) -> AsyncEngine:
        """
        Get the SQLAlchemy engine.

        Returns:
            AsyncEngine: Database engine
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        return self._engine

    @property
    def db_type(self) -> str:
        """Get the database type."""
        return self._db_type

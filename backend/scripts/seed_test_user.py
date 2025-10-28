"""
Seed script to create a test user in the database.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.core.logging import setup_logging, get_logger
from app.db.adapters import get_database_adapter, init_database, close_database
from app.db.models.user import User

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def seed_test_user():
    """Create a test user with email info@codedthemes.com and password 12345."""

    logger.info("Starting database seed...")

    try:
        # Initialize database
        await init_database()
        db_adapter = get_database_adapter()

        async for session in db_adapter.get_session():
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == "info@codedthemes.com")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.info("Test user already exists. Skipping seed.")
                print("✓ Test user already exists: info@codedthemes.com")
                return

            # Create test user
            test_user = User(
                username="testuser",
                email="info@codedthemes.com",
                password_hash=hash_password("12345"),
                first_name="Test",
                last_name="User",
                is_active=True,
                is_verified=True,
                is_superuser=False,
                failed_login_attempts=0,
            )

            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            logger.info(f"Test user created successfully with ID: {test_user.id}")
            print("\n" + "="*60)
            print("✓ Test user created successfully!")
            print("="*60)
            print(f"  Email:    info@codedthemes.com")
            print(f"  Password: 12345")
            print(f"  Username: testuser")
            print(f"  User ID:  {test_user.id}")
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        print(f"\n✗ Error: {e}\n")
        raise
    finally:
        await close_database()
        logger.info("Database seed complete")


if __name__ == "__main__":
    asyncio.run(seed_test_user())

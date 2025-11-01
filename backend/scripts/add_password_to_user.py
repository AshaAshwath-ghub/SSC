"""
Script to add/update password for an existing user.
This allows OAuth users to also log in with email/password.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.security import hash_password
from app.core.logging import setup_logging, get_logger
from app.db.adapters import get_database_adapter, init_database, close_database
from app.db.models.user import User

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def add_password_to_user():
    """Add password to existing user to enable local login."""

    logger.info("Starting password addition...")

    # User details
    email = "niteesh.kl@jillellagroup.com"
    new_password = "SecurePass123!"

    try:
        # Initialize database
        await init_database()
        db_adapter = get_database_adapter()

        async for session in db_adapter.get_session():
            # Find the user
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User {email} not found in database")
                print("\n" + "="*60)
                print(f"X User not found: {email}")
                print("="*60 + "\n")
                return

            # Check if user already has a password
            had_password = bool(user.password_hash)

            # Update password
            user.password_hash = hash_password(new_password)

            # Ensure user is active and verified
            user.is_active = True
            user.is_verified = True

            await session.commit()
            await session.refresh(user)

            logger.info(f"Password {'updated' if had_password else 'added'} for user {email}")
            print("\n" + "="*60)
            print(f"Password {'updated' if had_password else 'added'} successfully!")
            print("="*60)
            print(f"  User ID:   {user.id}")
            print(f"  Email:     {user.email}")
            print(f"  Username:  {user.username}")
            print(f"  Name:      {user.first_name} {user.last_name}")
            print(f"  Password:  {new_password}")
            print(f"  Active:    {user.is_active}")
            print(f"  Verified:  {user.is_verified}")
            print("="*60)
            print("\nUser can now log in using:")
            print("  1. Microsoft OAuth (existing)")
            print(f"  2. Email/Password:")
            print(f"     Email:    {email}")
            print(f"     Password: {new_password}")
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Error adding password: {e}", exc_info=True)
        print(f"\nX Error: {e}\n")
        raise
    finally:
        await close_database()
        logger.info("Password addition complete")


if __name__ == "__main__":
    asyncio.run(add_password_to_user())

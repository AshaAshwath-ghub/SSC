"""
Script to create a new user in the database.
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


async def create_niteesh_user():
    """Create Niteesh KL user in the database."""

    logger.info("Starting user creation...")

    # User details
    email = "niteesh.kl@jillellagroup.com"
    username = "niteeshkl"
    password = "SecurePass123!"
    first_name = "Niteesh"
    last_name = "KL"

    try:
        # Initialize database
        await init_database()
        db_adapter = get_database_adapter()

        async for session in db_adapter.get_session():
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.info(f"User {email} already exists. Skipping.")
                print("\n" + "="*60)
                print(f"✓ User already exists: {email}")
                print("="*60)
                print(f"  Email:    {existing_user.email}")
                print(f"  Username: {existing_user.username}")
                print(f"  User ID:  {existing_user.id}")
                print(f"  Active:   {existing_user.is_active}")
                print("="*60 + "\n")
                return

            # Create new user
            new_user = User(
                email=email,
                username=username,
                password_hash=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_verified=True,
                is_superuser=False,
                failed_login_attempts=0
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            logger.info(f"User created successfully with ID: {new_user.id}")
            print("\n" + "="*60)
            print("✓ User created successfully!")
            print("="*60)
            print(f"  Email:    {email}")
            print(f"  Password: {password}")
            print(f"  Username: {username}")
            print(f"  Name:     {first_name} {last_name}")
            print(f"  User ID:  {new_user.id}")
            print("="*60)
            print("\nUser can now log in with:")
            print(f"  Email:    {email}")
            print(f"  Password: {password}")
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        print(f"\n✗ Error: {e}\n")
        raise
    finally:
        await close_database()
        logger.info("User creation complete")


if __name__ == "__main__":
    asyncio.run(create_niteesh_user())

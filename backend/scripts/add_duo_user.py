"""
Script to add a Duo-enrolled user to the database.
This user should already be registered in Duo Push administration portal.
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.adapters import get_database_adapter
from app.db.models.user import User
from app.core.security import hash_password


async def add_duo_user():
    """Add a Duo-enrolled user to the database."""

    # User details
    email = "user@gmail.com"
    username = "duouser"
    password = "Test@123"  # Change this to a secure password
    first_name = "Duo"
    last_name = "User"

    print("=" * 60)
    print("Adding Duo-enrolled user to database")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Name: {first_name} {last_name}")
    print("=" * 60)

    # Get database adapter and initialize
    db_adapter = get_database_adapter()
    await db_adapter.init()

    async for session in db_adapter.get_session():
        try:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"\n[ERROR] User with email {email} already exists!")
                print(f"   User ID: {existing_user.id}")
                print(f"   Username: {existing_user.username}")
                print(f"   Active: {existing_user.is_active}")
                print(f"   Verified: {existing_user.is_verified}")
                return

            # Check if username already exists
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing_username = result.scalar_one_or_none()

            if existing_username:
                print(f"\n[ERROR] User with username {username} already exists!")
                print(f"   Trying with username: {username}_{email.split('@')[0]}")
                username = f"{username}_{email.split('@')[0]}"

            # Create new user
            print("\nCreating new user...")
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_verified=True,  # Mark as verified
                is_superuser=False,
                failed_login_attempts=0,
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            print("\n[SUCCESS] User created successfully!")
            print(f"   User ID: {new_user.id}")
            print(f"   Username: {new_user.username}")
            print(f"   Email: {new_user.email}")
            print(f"   Full Name: {new_user.full_name}")
            print(f"   Active: {new_user.is_active}")
            print(f"   Verified: {new_user.is_verified}")

            print("\n" + "=" * 60)
            print("IMPORTANT: Duo Push Configuration")
            print("=" * 60)
            print(f"Make sure this user is enrolled in Duo with username: {email}")
            print("The Duo username should match the email address.")
            print("\nTo test:")
            print(f"1. Navigate to the login page")
            print(f"2. Enter email: {email}")
            print(f"3. Enter password: {password}")
            print(f"4. Approve the Duo Push on your mobile device")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] Error creating user: {str(e)}")
            raise


if __name__ == "__main__":
    print("\nStarting user creation script...\n")
    asyncio.run(add_duo_user())
    print("\nScript completed!\n")

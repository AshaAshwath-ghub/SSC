"""
Add phone_number and duo_username fields to users table.
Run this script to update the database schema.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.adapters import init_database, get_database_adapter
from sqlalchemy import text


async def add_fields():
    """Add phone_number and duo_username fields to users table."""
    await init_database()
    adapter = get_database_adapter()

    async for session in adapter.get_session():
        try:
            # Check if columns already exist
            print("\n[INFO] Checking if columns already exist...")

            # Add phone_number column
            try:
                await session.execute(
                    text("""
                        ALTER TABLE users
                        ADD COLUMN phone_number VARCHAR(20)
                    """)
                )
                print("[SUCCESS] Added phone_number column")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("[INFO] phone_number column already exists")
                else:
                    print(f"[ERROR] Error adding phone_number: {e}")
                    raise

            # Add duo_username column
            try:
                await session.execute(
                    text("""
                        ALTER TABLE users
                        ADD COLUMN duo_username VARCHAR(255)
                    """)
                )
                print("[SUCCESS] Added duo_username column")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("[INFO] duo_username column already exists")
                else:
                    print(f"[ERROR] Error adding duo_username: {e}")
                    raise

            # Add index on duo_username
            try:
                await session.execute(
                    text("""
                        CREATE INDEX IF NOT EXISTS idx_users_duo_username
                        ON users(duo_username)
                    """)
                )
                print("[SUCCESS] Added index on duo_username column")
            except Exception as e:
                print(f"[WARNING] Error adding index: {e}")

            await session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("=" * 80)

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] Migration failed: {e}")
            raise

        break


if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MIGRATION: Add phone_number and duo_username to users")
    print("=" * 80)
    asyncio.run(add_fields())

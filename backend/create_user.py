import asyncio
from sqlalchemy import text
from app.core.security import hash_password
from app.db.adapters import get_database_adapter

async def create_user():
    # Hash the password properly
    password_hash = hash_password("SecurePass123!")

    # Get database adapter
    db_adapter = get_database_adapter()

    # Initialize database
    await db_adapter.init()

    # Get a session
    async for session in db_adapter.get_session():
        try:
            # Delete existing user if any
            await session.execute(
                text("DELETE FROM users WHERE email = 'niteesh.kl@jillellagroup.com'")
            )
            await session.commit()

            # Create new user
            await session.execute(
                text("""
                INSERT INTO users (
                    id, username, email, password_hash, first_name, last_name,
                    is_active, is_verified, is_superuser, failed_login_attempts,
                    created_at, updated_at
                ) VALUES (
                    2, 'niteesh.kl', 'niteesh.kl@jillellagroup.com', :password_hash,
                    'Niteesh', 'KL', true, true, true, 0, NOW(), NOW()
                )
                ON CONFLICT (id) DO UPDATE SET
                    password_hash = :password_hash,
                    username = 'niteesh.kl',
                    email = 'niteesh.kl@jillellagroup.com',
                    is_active = true,
                    is_verified = true,
                    updated_at = NOW()
                """),
                {"password_hash": password_hash}
            )
            await session.commit()

            print(f"User created/updated successfully!")
            print(f"Email: niteesh.kl@jillellagroup.com")
            print(f"Password: SecurePass123!")
            print(f"Password hash: {password_hash}")
            break
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
            raise

    # Close database
    await db_adapter.close()

if __name__ == "__main__":
    asyncio.run(create_user())

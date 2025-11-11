"""
Check users and their phone numbers in the database.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.adapters import get_database_adapter
from sqlalchemy import text


async def check_users():
    """Check all users and their phone numbers."""
    from app.db.adapters import init_database
    await init_database()

    adapter = get_database_adapter()
    async for session in adapter.get_session():
        result = await session.execute(
            text('SELECT id, username, email, phone_number, duo_username FROM users ORDER BY id')
        )
        users = result.fetchall()

        print('\n' + '=' * 120)
        print('USERS IN DATABASE')
        print('=' * 120)
        print(f"{'ID':<5} {'Username':<20} {'Email':<35} {'Phone':<20} {'Duo Username':<20}")
        print('-' * 120)

        for user in users:
            phone = user[3] if user[3] else "NOT SET"
            duo = user[4] if user[4] else "NOT SET"
            print(f"{user[0]:<5} {user[1]:<20} {user[2]:<35} {phone:<20} {duo:<20}")

        print('=' * 120)
        print(f"Total users: {len(users)}")
        print('=' * 120 + '\n')

        break


if __name__ == "__main__":
    asyncio.run(check_users())

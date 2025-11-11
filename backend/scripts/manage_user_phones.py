"""
Manage user phone numbers for Twilio SMS integration.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.adapters import init_database, get_database_adapter
from sqlalchemy import text


async def list_users():
    """List all users with their current phone numbers."""
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


async def update_phone_number(user_id: int, phone_number: str):
    """Update phone number for a user."""
    await init_database()
    adapter = get_database_adapter()

    async for session in adapter.get_session():
        try:
            await session.execute(
                text('UPDATE users SET phone_number = :phone WHERE id = :id'),
                {'phone': phone_number, 'id': user_id}
            )
            await session.commit()
            print(f"[SUCCESS] Updated phone number for user ID {user_id} to {phone_number}")
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Failed to update phone: {e}")
            raise

        break


async def update_duo_username(user_id: int, duo_username: str):
    """Update Duo username for a user."""
    await init_database()
    adapter = get_database_adapter()

    async for session in adapter.get_session():
        try:
            await session.execute(
                text('UPDATE users SET duo_username = :duo WHERE id = :id'),
                {'duo': duo_username, 'id': user_id}
            )
            await session.commit()
            print(f"[SUCCESS] Updated Duo username for user ID {user_id} to {duo_username}")
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Failed to update Duo username: {e}")
            raise

        break


async def bulk_update():
    """Bulk update phone numbers and Duo usernames for all users."""
    await init_database()
    adapter = get_database_adapter()

    # Example phone numbers - adjust these for your users
    updates = [
        {'id': 1, 'phone': '+19876543210', 'duo': 'admin'},
        {'id': 2, 'phone': '+19876543211', 'duo': 'testuser'},
        {'id': 3, 'phone': '+19876543212', 'duo': 'demo'},
        {'id': 4, 'phone': '+19876543213', 'duo': 'demouser'},
        {'id': 5, 'phone': '+19876543214', 'duo': 'aastha.bhandari@jillellagroup.com'},
        {'id': 6, 'phone': '+19876543215', 'duo': 'akash.jillella@jillellagroup.com'},
        {'id': 7, 'phone': '+19876543216', 'duo': 'shruti.potru@jillellagroup.com'},
        {'id': 8, 'phone': '+19876543217', 'duo': 'jayendhar.bomma@jillellagroup.com'},
        {'id': 9, 'phone': '+19876543218', 'duo': 'asha.ashwathappa@jillellagroup.com'},
    ]

    async for session in adapter.get_session():
        try:
            for update in updates:
                try:
                    result = await session.execute(
                        text('UPDATE users SET phone_number = :phone, duo_username = :duo WHERE id = :id'),
                        {'phone': update['phone'], 'duo': update['duo'], 'id': update['id']}
                    )
                    if result.rowcount > 0:
                        print(f"[SUCCESS] Updated user ID {update['id']}: phone={update['phone']}, duo={update['duo']}")
                    else:
                        print(f"[INFO] User ID {update['id']} not found, skipping")
                except Exception as e:
                    print(f"[ERROR] Failed to update user ID {update['id']}: {e}")

            await session.commit()
            print("\n[SUCCESS] Bulk update completed!")
        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] Bulk update failed: {e}")
            raise

        break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Manage user phone numbers')
    parser.add_argument('action', choices=['list', 'update', 'bulk'], help='Action to perform')
    parser.add_argument('--user-id', type=int, help='User ID (for update action)')
    parser.add_argument('--phone', help='Phone number in E.164 format (e.g., +1234567890)')
    parser.add_argument('--duo', help='Duo username')

    args = parser.parse_args()

    if args.action == 'list':
        asyncio.run(list_users())
    elif args.action == 'update':
        if not args.user_id:
            print("[ERROR] --user-id is required for update action")
            sys.exit(1)
        if args.phone:
            asyncio.run(update_phone_number(args.user_id, args.phone))
        if args.duo:
            asyncio.run(update_duo_username(args.user_id, args.duo))
    elif args.action == 'bulk':
        print("=" * 120)
        print("BULK UPDATE: Adding phone numbers and Duo usernames to all users")
        print("=" * 120)
        asyncio.run(bulk_update())

"""
Update specific user phone numbers for Twilio SMS integration.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.adapters import init_database, get_database_adapter
from sqlalchemy import text


async def update_phones():
    """Update phone numbers for specific users."""
    await init_database()
    adapter = get_database_adapter()

    # Phone number mappings (E.164 format)
    updates = [
        {
            'email': 'asha.ashwathappa@jillellagroup.com',
            'phone': '+918553724128',
            'duo': 'asha.ashwathappa@jillellagroup.com'
        },
        {
            'email': 'niteesh.kl@jillellagroup.com',
            'phone': '+919113943553',
            'duo': 'niteesh.kl@jillellagroup.com'
        },
        {
            'email': 'jayendhar.murali@jillellagroup.com',
            'phone': '+919980092904',
            'duo': 'jayendhar.murali@jillellagroup.com'
        }
    ]

    async for session in adapter.get_session():
        try:
            print("\n" + "=" * 120)
            print("UPDATING USER PHONE NUMBERS AND DUO USERNAMES")
            print("=" * 120 + "\n")

            for update in updates:
                result = await session.execute(
                    text('''
                        UPDATE users
                        SET phone_number = :phone, duo_username = :duo
                        WHERE email = :email
                    '''),
                    {'phone': update['phone'], 'duo': update['duo'], 'email': update['email']}
                )

                if result.rowcount > 0:
                    print(f"[SUCCESS] Updated {update['email']}")
                    print(f"          Phone: {update['phone']}")
                    print(f"          Duo: {update['duo']}\n")
                else:
                    print(f"[WARNING] User not found: {update['email']}\n")

            await session.commit()

            print("=" * 120)
            print("UPDATE COMPLETED - Verifying changes...")
            print("=" * 120 + "\n")

            # Verify the updates
            result = await session.execute(
                text('''
                    SELECT id, username, email, phone_number, duo_username
                    FROM users
                    WHERE email IN (:email1, :email2, :email3)
                    ORDER BY id
                '''),
                {
                    'email1': updates[0]['email'],
                    'email2': updates[1]['email'],
                    'email3': updates[2]['email']
                }
            )
            users = result.fetchall()

            print(f"{'ID':<5} {'Username':<20} {'Email':<35} {'Phone':<20} {'Duo Username':<30}")
            print('-' * 120)
            for user in users:
                phone = user[3] if user[3] else "NOT SET"
                duo = user[4] if user[4] else "NOT SET"
                print(f"{user[0]:<5} {user[1]:<20} {user[2]:<35} {phone:<20} {duo:<30}")

            print("=" * 120 + "\n")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] Update failed: {e}")
            raise

        break


if __name__ == "__main__":
    asyncio.run(update_phones())

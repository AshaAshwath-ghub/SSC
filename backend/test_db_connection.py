"""
Test database connection.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings

async def test_connection():
    """Test database connection."""
    print(f"Testing connection to database...")
    print(f"  DB Type: {settings.db_type}")
    print(f"  DB Host: {settings.db_host}")
    print(f"  DB Port: {settings.db_port}")
    print(f"  DB User: {settings.db_user}")
    print(f"  DB Password: {'*' * len(settings.db_password)}")
    print(f"  DB Name: {settings.db_name}")
    print(f"  Database URL: {settings.database_url}")

    try:
        import asyncpg
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        )
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print(f"\n✓ Connection successful! Result: {result}")
        return True
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

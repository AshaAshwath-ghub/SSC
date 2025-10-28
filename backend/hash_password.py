"""Generate hashed password for test user."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import hash_password

password = "12345"
hashed = hash_password(password)
print(f"Password: {password}")
print(f"Hashed:  {hashed}")

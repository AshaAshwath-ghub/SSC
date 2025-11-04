"""
Test Twilio service initialization.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

print("=" * 80)
print("TWILIO CONFIGURATION TEST")
print("=" * 80)
print(f"\nAccount SID: {settings.twilio_account_sid[:10]}... (length: {len(settings.twilio_account_sid)})")
print(f"Auth Token: {settings.twilio_auth_token[:10]}... (length: {len(settings.twilio_auth_token)})")
print(f"Phone Number: {settings.twilio_phone_number}")
print("\n" + "=" * 80)

# Test Twilio service initialization
try:
    from app.core.twilio_service import get_twilio_service

    print("\n[INFO] Initializing Twilio service...")
    service = get_twilio_service()
    print(f"[SUCCESS] Twilio service initialized!")
    print(f"[SUCCESS] From Phone: {service.from_phone}")
    print(f"[SUCCESS] Account SID: {service.account_sid[:10]}...")

except ValueError as e:
    print(f"\n[ERROR] Configuration Error: {e}")
except Exception as e:
    print(f"\n[ERROR] Unexpected Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

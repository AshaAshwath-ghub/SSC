"""
Twilio SMS service for sending OTP via SMS.
"""
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Service for sending SMS via Twilio."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: Optional[str] = None
    ):
        """
        Initialize Twilio service.

        Args:
            account_sid: Twilio Account SID (defaults to TWILIO_ACCOUNT_SID env var)
            auth_token: Twilio Auth Token (defaults to TWILIO_AUTH_TOKEN env var)
            from_phone: Twilio phone number (defaults to TWILIO_PHONE_NUMBER env var)
        """
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.from_phone = from_phone or settings.twilio_phone_number

        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured")
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables are required")

        if not self.from_phone:
            logger.warning("Twilio phone number not configured")
            raise ValueError("TWILIO_PHONE_NUMBER environment variable is required")

        self.client = Client(self.account_sid, self.auth_token)
        logger.info(f"Twilio service initialized with phone: {self.from_phone}")

    async def send_otp_sms(
        self,
        to_phone: str,
        otp_code: str,
        username: Optional[str] = None
    ) -> dict:
        """
        Send OTP verification SMS.

        Args:
            to_phone: Recipient phone number (E.164 format, e.g., +1234567890)
            otp_code: One-time password code
            username: Optional username for personalization

        Returns:
            dict: Response with status and message
                - status: 'success', 'error', or 'invalid_phone'
                - message: Status message
                - sid: Twilio message SID (if successful)
        """
        try:
            # Validate phone number format
            if not to_phone.startswith('+'):
                logger.warning(f"Invalid phone number format: {to_phone}")
                return {
                    "status": "invalid_phone",
                    "message": "Phone number must be in E.164 format (e.g., +1234567890)"
                }

            # Create SMS message
            message_body = f"""Your verification code is: {otp_code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this message.

- Your Security Team"""

            # Send SMS via Twilio
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_phone,
                to=to_phone
            )

            logger.info(f"OTP SMS sent successfully to {to_phone}. SID: {message.sid}")

            return {
                "status": "success",
                "message": "SMS sent successfully",
                "sid": message.sid
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {e.msg}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to send SMS: {e.msg}",
                "error_code": e.code
            }

        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_phone}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": "Failed to send SMS due to an unexpected error"
            }

    async def verify_phone_number(self, phone: str) -> bool:
        """
        Check if a phone number is valid format.

        Args:
            phone: Phone number to validate

        Returns:
            bool: True if valid format, False otherwise
        """
        try:
            # Basic validation - phone should start with + and be followed by digits
            if not phone.startswith('+'):
                return False

            # Remove + and check if remaining chars are digits
            phone_digits = phone[1:]
            if not phone_digits.isdigit():
                return False

            # Check length (international numbers are typically 10-15 digits)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating phone number: {str(e)}")
            return False


# Singleton instance
_twilio_service: Optional[TwilioService] = None


def get_twilio_service() -> TwilioService:
    """Get or create Twilio service instance."""
    global _twilio_service
    if _twilio_service is None:
        _twilio_service = TwilioService()
    return _twilio_service

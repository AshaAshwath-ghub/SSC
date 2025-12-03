"""
Duo Security integration for two-factor authentication.
Provides Duo Push notification authentication functionality.
"""
import duo_client
from typing import Dict, Optional, Literal
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DuoSecurityService:
    """Service for handling Duo Security authentication."""

    def __init__(self):
        """Initialize Duo Auth API client."""
        if not all([settings.duo_auth_ikey, settings.duo_auth_skey, settings.duo_auth_host]):
            raise ValueError("Duo Auth API credentials not configured")

        self.auth_api = duo_client.Auth(
            ikey=settings.duo_auth_ikey,
            skey=settings.duo_auth_skey,
            host=settings.duo_auth_host,
        )
        logger.info("Duo Security service initialized")

    async def send_push_notification(
        self,
        username: str,
        device: str = "auto",
        push_type: str = "Login Request",
        push_info: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Send a push notification to user's device via Duo.

        Args:
            username: Duo username (typically email or username)
            device: Device identifier or "auto" for auto-select
            push_type: Type of authentication request
            push_info: Additional information to display in push (optional)

        Returns:
            Dictionary with authentication result

        Example response:
            {
                "result": "allow" | "deny",
                "status": "pushed" | "answered",
                "status_msg": "Success. Logging you in..."
            }
        """
        try:
            logger.info(f"Sending Duo push notification to user: {username}")

            # Prepare push info (additional context shown to user)
            # Note: Duo API is very strict about pushinfo format - skip if None
            if push_info is None or not push_info:
                logger.info(f"Sending Duo push without pushinfo")
                # Call Duo Auth API to send push WITHOUT pushinfo
                response = self.auth_api.auth(
                    factor="push",
                    username=username,
                    device=device,
                    type=push_type
                )
            else:
                # Ensure all pushinfo values are strings
                clean_push_info = {}
                for key, value in push_info.items():
                    clean_push_info[str(key)] = str(value) if value is not None else ""

                logger.info(f"Push info being sent: {clean_push_info}")

                # Call Duo Auth API to send push WITH pushinfo
                response = self.auth_api.auth(
                    factor="push",
                    username=username,
                    device=device,
                    type=push_type,
                    pushinfo=clean_push_info
                )

            logger.info(f"Duo push response for {username}: {response.get('result')}")

            return {
                "result": response.get("result"),  # "allow" or "deny"
                "status": response.get("status"),  # "pushed", "answered", etc.
                "status_msg": response.get("status_msg", ""),
                "trusted_device_token": response.get("trusted_device_token"),
            }

        except RuntimeError as e:
            logger.error(f"Duo API error for user {username}: {str(e)}")
            return {
                "result": "error",
                "status": "error",
                "status_msg": f"Duo authentication error: {str(e)}",
                "trusted_device_token": None,
            }
        except Exception as e:
            logger.error(f"Unexpected error during Duo push for {username}: {str(e)}", exc_info=True)
            return {
                "result": "error",
                "status": "error",
                "status_msg": "An unexpected error occurred",
                "trusted_device_token": None,
            }

    async def send_phone_call(self, username: str, device: str = "auto") -> Dict:
        """
        Send a phone call to user's device via Duo.

        Args:
            username: Duo username
            device: Device identifier or "auto" for auto-select

        Returns:
            Dictionary with authentication result
        """
        try:
            logger.info(f"Sending Duo phone call to user: {username}")

            # Call Duo Auth API to send phone call
            response = self.auth_api.auth(
                factor="phone",
                username=username,
                device=device
            )

            logger.info(f"Duo phone call response for {username}: {response.get('result')}")

            return {
                "result": response.get("result"),
                "status": response.get("status"),
                "status_msg": response.get("status_msg", ""),
            }

        except RuntimeError as e:
            logger.error(f"Duo API error for phone call {username}: {str(e)}")
            return {
                "result": "error",
                "status": "error",
                "status_msg": f"Duo phone call error: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error during Duo phone call for {username}: {str(e)}", exc_info=True)
            return {
                "result": "error",
                "status": "error",
                "status_msg": "An unexpected error occurred",
            }

    async def send_sms(self, username: str, device: str = "auto") -> Dict:
        """
        Send an SMS passcode to user's device via Duo.

        Args:
            username: Duo username
            device: Device identifier or "auto" for auto-select

        Returns:
            Dictionary with authentication result
        """
        try:
            logger.info(f"Sending Duo SMS to user: {username}")

            # Call Duo Auth API to send SMS
            response = self.auth_api.auth(
                factor="sms",
                username=username,
                device=device
            )

            logger.info(f"Duo SMS response for {username}: {response.get('result')}")

            return {
                "result": response.get("result"),
                "status": response.get("status"),
                "status_msg": response.get("status_msg", ""),
            }

        except RuntimeError as e:
            logger.error(f"Duo API error for SMS {username}: {str(e)}")
            return {
                "result": "error",
                "status": "error",
                "status_msg": f"Duo SMS error: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error during Duo SMS for {username}: {str(e)}", exc_info=True)
            return {
                "result": "error",
                "status": "error",
                "status_msg": "An unexpected error occurred",
            }

    async def verify_otp(self, username: str, passcode: str) -> Dict:
        """
        Verify a one-time passcode (OTP) from Duo Mobile app.

        Args:
            username: Duo username
            passcode: 6-digit passcode from Duo Mobile app

        Returns:
            Dictionary with verification result
        """
        try:
            logger.info(f"Verifying Duo OTP for user: {username}")

            response = self.auth_api.auth(
                factor="passcode",
                username=username,
                passcode=passcode
            )

            return {
                "result": response.get("result"),
                "status": response.get("status"),
                "status_msg": response.get("status_msg", ""),
            }

        except RuntimeError as e:
            logger.error(f"Duo OTP verification error for {username}: {str(e)}")
            return {
                "result": "error",
                "status": "error",
                "status_msg": f"Verification error: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification for {username}: {str(e)}", exc_info=True)
            return {
                "result": "error",
                "status": "error",
                "status_msg": "An unexpected error occurred",
            }

    async def check_user_status(self, username: str) -> Dict:
        """
        Check if a user is enrolled in Duo.

        Args:
            username: Duo username

        Returns:
            Dictionary with enrollment status
        """
        try:
            # Perform a preauth check
            logger.info(f"Checking Duo enrollment status for user: {username}")
            response = self.auth_api.preauth(username=username)

            result = response.get("result")
            status_msg = response.get("status_msg", "")
            devices = response.get("devices", [])

            logger.info(f"Duo preauth response for {username}: result={result}, status={status_msg}, devices_count={len(devices)}")

            enrolled = result == "auth"

            return {
                "enrolled": enrolled,
                "status": status_msg,
                "devices": devices,
                "result": result,  # Include the raw result for debugging
            }

        except RuntimeError as e:
            logger.error(f"Duo API error checking status for {username}: {str(e)}", exc_info=True)
            return {
                "enrolled": False,
                "status": f"Error: {str(e)}",
                "devices": [],
                "result": "error",
            }
        except Exception as e:
            logger.error(f"Unexpected error checking Duo status for {username}: {str(e)}", exc_info=True)
            return {
                "enrolled": False,
                "status": "An unexpected error occurred",
                "devices": [],
                "result": "error",
            }

    async def get_user_devices(self, username: str) -> list:
        """
        Get list of Duo devices registered for a user.

        Args:
            username: Duo username

        Returns:
            List of device dictionaries
        """
        try:
            response = self.auth_api.preauth(username=username)
            return response.get("devices", [])

        except Exception as e:
            logger.error(f"Error fetching devices for {username}: {str(e)}")
            return []


# Global Duo service instance
duo_service: Optional[DuoSecurityService] = None


def get_duo_service() -> DuoSecurityService:
    """
    Get or create the global Duo Security service instance.

    Returns:
        DuoSecurityService instance

    Raises:
        ValueError: If Duo credentials are not configured
    """
    global duo_service

    if duo_service is None:
        duo_service = DuoSecurityService()

    return duo_service

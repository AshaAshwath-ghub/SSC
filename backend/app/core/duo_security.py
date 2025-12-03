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
        """Initialize Duo Auth API and Admin API clients."""
        if not all([settings.duo_auth_ikey, settings.duo_auth_skey, settings.duo_auth_host]):
            raise ValueError("Duo Auth API credentials not configured")

        self.auth_api = duo_client.Auth(
            ikey=settings.duo_auth_ikey,
            skey=settings.duo_auth_skey,
            host=settings.duo_auth_host,
        )

        # Initialize Admin API for user enrollment management
        if all([settings.duo_admin_ikey, settings.duo_admin_skey, settings.duo_admin_host]):
            self.admin_api = duo_client.Admin(
                ikey=settings.duo_admin_ikey,
                skey=settings.duo_admin_skey,
                host=settings.duo_admin_host,
            )
            logger.info("Duo Security service initialized (Auth + Admin APIs)")
        else:
            self.admin_api = None
            logger.warning("Duo Admin API not configured - enrollment features disabled")
            logger.info("Duo Security service initialized (Auth API only)")

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

    async def send_enrollment_sms(self, username: str, phone_number: Optional[str] = None) -> Dict:
        """
        Send enrollment SMS to user via Duo Admin API.

        This allows users who haven't set up Duo yet to receive an SMS
        with a link to enroll their device (install Duo Mobile and register).

        Args:
            username: Duo username (email or username)
            phone_number: Optional phone number (if not already in Duo)

        Returns:
            Dictionary with enrollment result:
                - success (bool): Whether SMS was sent
                - message (str): User-friendly message
                - activation_url (str): Enrollment URL (optional)

        Example:
            {
                "success": True,
                "message": "Enrollment SMS sent to +1XXX...X789",
                "activation_url": "https://api-xxx.duosecurity.com/portal?code=..."
            }
        """
        if not self.admin_api:
            logger.error("Duo Admin API not configured - cannot send enrollment SMS")
            return {
                "success": False,
                "message": "Duo enrollment is not configured. Please contact your administrator."
            }

        try:
            logger.info(f"Sending Duo enrollment SMS to user: {username}")

            # First, find the user in Duo by username or email
            users = self.admin_api.get_users()
            duo_user = None

            for user in users:
                if user.get("username") == username or user.get("email") == username:
                    duo_user = user
                    break

            if not duo_user:
                logger.warning(f"User {username} not found in Duo - cannot send enrollment SMS")
                return {
                    "success": False,
                    "message": "User not found in Duo system. Please contact your administrator to add you."
                }

            user_id = duo_user.get("user_id")
            logger.info(f"Found Duo user: {username} (ID: {user_id})")

            # Check if user already has phones registered
            phones = self.admin_api.get_user_phones(user_id)

            if not phones:
                logger.info(f"No phones found for user {user_id}, cannot send SMS")
                return {
                    "success": False,
                    "message": "No phone number registered. Please contact your administrator to add your phone number first."
                }

            # Use the first phone
            phone = phones[0]
            phone_id = phone.get("phone_id")
            phone_number_display = phone.get("number", "your phone")
            phone_activated = phone.get("activated", False)
            phone_capabilities = phone.get("capabilities", [])

            logger.info(f"Phone details for {username}: phone_id={phone_id}, number={phone_number_display}, activated={phone_activated}, capabilities={phone_capabilities}")
            logger.info(f"Full phone object: {phone}")

            # Check if phone is already activated
            if phone_activated:
                logger.warning(f"Phone {phone_id} is already activated - cannot send activation SMS again")
                return {
                    "success": False,
                    "message": "Your phone is already activated in Duo. Please install Duo Mobile app and it should work automatically. If you're having issues, contact your administrator to reset your device."
                }

            logger.info(f"Sending enrollment SMS to phone {phone_id} ({phone_number_display})")
            logger.info(f"Phone activation_url: {activation_url}")

            # Try to send activation SMS via Duo Admin API
            try:
                # This sends an SMS with a link to activate Duo Mobile
                response = self.admin_api.send_sms_activation_to_phone(phone_id)

                logger.info(f"Duo enrollment SMS sent successfully to {username}")

                # Mask phone number for security
                masked_phone = f"+{phone_number_display[:2]}XXX...X{phone_number_display[-3:]}" if len(phone_number_display) > 5 else "your phone"

                return {
                    "success": True,
                    "message": f"Enrollment instructions sent to {masked_phone}. Please check your phone and follow the link to install Duo Mobile.",
                    "activation_url": response.get("activation_url") if response else activation_url
                }

            except RuntimeError as e:
                error_msg = str(e)

                # If 403 and we have activation URL, return it directly instead of failing
                if ("403" in error_msg or "forbidden" in error_msg.lower()) and activation_url:
                    logger.warning(f"SMS send failed with 403 but activation_url available - providing URL directly: {activation_url}")

                    return {
                        "success": True,
                        "message": "Unable to send SMS automatically. Please copy this link and open it in your browser to activate Duo Mobile:",
                        "activation_url": activation_url,
                        "manual_enrollment": True  # Flag to show URL in UI
                    }
                else:
                    # Re-raise for other errors
                    raise

        except RuntimeError as e:
            error_msg = str(e)
            logger.error(f"Duo Admin API error sending enrollment SMS for {username}: {error_msg}")
            return {
                "success": False,
                "message": f"Failed to send enrollment SMS: {error_msg}"
            }
        except Exception as e:
            logger.error(f"Unexpected error sending enrollment SMS for {username}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": "An unexpected error occurred while sending enrollment instructions."
            }


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

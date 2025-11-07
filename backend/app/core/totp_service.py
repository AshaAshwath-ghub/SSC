"""
TOTP (Time-based One-Time Password) service for authenticator app integration.
Supports Google Authenticator, Authy, Microsoft Authenticator, etc.
"""
from typing import Optional, Dict, List
import pyotp
import qrcode
import secrets
import hashlib
from io import BytesIO
import base64
from datetime import datetime
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TOTPService:
    """Service for TOTP-based two-factor authentication."""

    def __init__(
        self,
        issuer_name: Optional[str] = None,
        interval: int = 30,
        digits: int = 6,
        window: int = 1
    ):
        """
        Initialize TOTP service.

        Args:
            issuer_name: Name of the application (e.g., "MyApp" or "Acme Corp")
            interval: Time step in seconds (default: 30)
            digits: Number of digits in OTP (default: 6)
            window: Number of time steps to check before/after current (default: 1)
        """
        self.issuer_name = issuer_name or getattr(settings, 'totp_issuer_name', 'SSC App')
        self.interval = interval
        self.digits = digits
        self.window = window
        logger.info(f"TOTP service initialized with issuer: {self.issuer_name}")

    def generate_secret(self) -> str:
        """
        Generate a random base32-encoded secret for TOTP.

        Returns:
            str: Base32-encoded secret (32 characters)
        """
        secret = pyotp.random_base32()
        logger.debug(f"Generated new TOTP secret: {secret[:8]}...")
        return secret

    def create_totp(self, secret: str) -> pyotp.TOTP:
        """
        Create a TOTP instance with the given secret.

        Args:
            secret: Base32-encoded secret

        Returns:
            pyotp.TOTP: TOTP instance
        """
        return pyotp.TOTP(
            secret,
            interval=self.interval,
            digits=self.digits
        )

    def generate_current_otp(self, secret: str) -> str:
        """
        Generate the current OTP for a given secret.
        Useful for testing or admin purposes.

        Args:
            secret: Base32-encoded TOTP secret

        Returns:
            str: Current OTP code
        """
        totp = self.create_totp(secret)
        return totp.now()

    def verify_otp(
        self,
        secret: str,
        otp_code: str,
        for_time: Optional[datetime] = None
    ) -> bool:
        """
        Verify a TOTP code against a secret.

        Args:
            secret: Base32-encoded TOTP secret
            otp_code: User-provided OTP code
            for_time: Optional specific time to verify against (default: now)

        Returns:
            bool: True if OTP is valid, False otherwise
        """
        try:
            totp = self.create_totp(secret)

            # Verify with time window (allows ±window * interval seconds)
            is_valid = totp.verify(
                otp_code,
                for_time=for_time,
                valid_window=self.window
            )

            if is_valid:
                logger.info(f"TOTP verification successful for secret: {secret[:8]}...")
            else:
                logger.warning(f"TOTP verification failed for secret: {secret[:8]}...")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying TOTP: {str(e)}", exc_info=True)
            return False

    def generate_provisioning_uri(
        self,
        secret: str,
        account_name: str,
        issuer_name: Optional[str] = None
    ) -> str:
        """
        Generate a provisioning URI for authenticator apps.
        This URI is used to generate QR codes.

        Args:
            secret: Base32-encoded TOTP secret
            account_name: User's email or username
            issuer_name: Override default issuer name

        Returns:
            str: Provisioning URI (otpauth://totp/...)
        """
        totp = self.create_totp(secret)
        issuer = issuer_name or self.issuer_name

        uri = totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )

        logger.debug(f"Generated provisioning URI for {account_name}")
        return uri

    def generate_qr_code(
        self,
        secret: str,
        account_name: str,
        issuer_name: Optional[str] = None
    ) -> str:
        """
        Generate a QR code image (base64-encoded) for TOTP setup.

        Args:
            secret: Base32-encoded TOTP secret
            account_name: User's email or username
            issuer_name: Override default issuer name

        Returns:
            str: Base64-encoded PNG image of QR code
        """
        try:
            # Generate provisioning URI
            uri = self.generate_provisioning_uri(secret, account_name, issuer_name)

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)

            # Generate image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()

            logger.info(f"Generated QR code for {account_name}")
            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
            raise

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.

        Args:
            count: Number of backup codes to generate (default: 10)

        Returns:
            List[str]: List of backup codes (format: XXXX-XXXX-XXXX)
        """
        codes = []
        for _ in range(count):
            # Generate 12-digit code
            code = ''.join([str(secrets.randbelow(10)) for _ in range(12)])
            # Format as XXXX-XXXX-XXXX
            formatted_code = f"{code[0:4]}-{code[4:8]}-{code[8:12]}"
            codes.append(formatted_code)

        logger.info(f"Generated {count} backup codes")
        return codes

    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for secure storage.

        Args:
            code: Backup code to hash

        Returns:
            str: SHA-256 hash of the code
        """
        # Remove dashes before hashing
        clean_code = code.replace('-', '')
        return hashlib.sha256(clean_code.encode()).hexdigest()

    def verify_backup_code(self, code: str, hashed_code: str) -> bool:
        """
        Verify a backup code against its hash.

        Args:
            code: User-provided backup code
            hashed_code: Stored hash of the backup code

        Returns:
            bool: True if code matches hash, False otherwise
        """
        try:
            computed_hash = self.hash_backup_code(code)
            is_valid = computed_hash == hashed_code

            if is_valid:
                logger.info(f"Backup code verification successful")
            else:
                logger.warning(f"Backup code verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying backup code: {str(e)}", exc_info=True)
            return False

    async def setup_totp_for_user(
        self,
        user_email: str,
        issuer_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Complete TOTP setup flow for a user.

        Args:
            user_email: User's email address
            issuer_name: Override default issuer name

        Returns:
            dict: Contains secret, qr_code_base64, provisioning_uri, and backup_codes
        """
        try:
            # Generate secret
            secret = self.generate_secret()

            # Generate QR code
            qr_code = self.generate_qr_code(secret, user_email, issuer_name)

            # Generate provisioning URI (for manual entry)
            uri = self.generate_provisioning_uri(secret, user_email, issuer_name)

            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            backup_codes_hashed = [self.hash_backup_code(code) for code in backup_codes]

            logger.info(f"TOTP setup completed for user: {user_email}")

            return {
                "secret": secret,
                "qr_code": qr_code,
                "provisioning_uri": uri,
                "backup_codes": backup_codes,  # Plain text (show once to user)
                "backup_codes_hashed": backup_codes_hashed  # Store these in DB
            }

        except Exception as e:
            logger.error(f"Error setting up TOTP for {user_email}: {str(e)}", exc_info=True)
            raise


# Singleton instance
_totp_service: Optional[TOTPService] = None


def get_totp_service() -> TOTPService:
    """Get or create TOTP service instance."""
    global _totp_service
    if _totp_service is None:
        _totp_service = TOTPService()
    return _totp_service

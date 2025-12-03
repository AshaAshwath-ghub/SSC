"""
Authentication schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    recaptcha_token: Optional[str] = Field(None, description="reCAPTCHA token (optional for now)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "info@codedthemes.com",
                    "password": "12345"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: Optional[str] = Field(None, description="JWT access token (only provided after MFA)")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token (only provided after MFA)")
    token_type: str = Field(default="bearer", description="Token type")
    user: Optional[UserResponse] = Field(None, description="User information (only provided after MFA)")
    requires_mfa: bool = Field(default=False, description="Whether MFA is required")
    mfa_token: Optional[str] = Field(None, description="Temporary token for MFA verification")
    mfa_method: Optional[str] = Field(None, description="MFA method required (e.g., 'duo_push', 'selection')")
    available_mfa_methods: Optional[List[str]] = Field(None, description="Available MFA methods user can choose from")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "username": "testuser",
                        "email": "info@codedthemes.com",
                        "is_active": True,
                        "is_verified": True
                    },
                    "requires_mfa": False
                }
            ]
        }
    }


class MFATriggerRequest(BaseModel):
    """Request to trigger a specific MFA method."""

    mfa_token: str = Field(..., description="Temporary MFA token from login response")
    method: str = Field(..., description="MFA method to trigger: 'duo_push', 'duo_phone', 'duo_sms', 'email_otp'")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mfa_token": "temp_mfa_token_here",
                    "method": "duo_push"
                }
            ]
        }
    }


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""

    mfa_token: str = Field(..., description="Temporary MFA token from login response")
    passcode: Optional[str] = Field(None, description="Optional OTP passcode (if not using push)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mfa_token": "temp_mfa_token_here",
                    "passcode": "123456"
                }
            ]
        }
    }


class MFAStatusResponse(BaseModel):
    """MFA push notification status response."""

    status: str = Field(..., description="Push status: 'pending', 'approved', 'denied', 'error'")
    message: str = Field(..., description="Status message")
    access_token: Optional[str] = Field(None, description="Access token if approved")
    refresh_token: Optional[str] = Field(None, description="Refresh token if approved")
    user: Optional[UserResponse] = Field(None, description="User info if approved")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "pending",
                    "message": "Waiting for push approval..."
                },
                {
                    "status": "approved",
                    "message": "Login successful",
                    "access_token": "eyJhbGc...",
                    "refresh_token": "eyJhbGc...",
                    "user": {"id": 1, "username": "testuser", "email": "test@example.com"}
                }
            ]
        }
    }


class TOTPSetupRequest(BaseModel):
    """Request to initiate TOTP setup."""

    user_email: Optional[EmailStr] = Field(None, description="User email (optional, can be derived from token)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_email": "user@example.com"
                }
            ]
        }
    }


class TOTPSetupResponse(BaseModel):
    """Response for TOTP setup with QR code and secret."""

    secret: str = Field(..., description="Base32-encoded TOTP secret")
    qr_code: str = Field(..., description="Base64-encoded QR code image (data URI)")
    provisioning_uri: str = Field(..., description="Provisioning URI for manual entry")
    backup_codes: List[str] = Field(..., description="Backup recovery codes (show once)")
    issuer_name: str = Field(..., description="Application name shown in authenticator app")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "secret": "JBSWY3DPEHPK3PXP",
                    "qr_code": "data:image/png;base64,iVBORw0KG...",
                    "provisioning_uri": "otpauth://totp/SSC%20App:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=SSC%20App",
                    "backup_codes": ["1234-5678-9012", "2345-6789-0123"],
                    "issuer_name": "SSC App"
                }
            ]
        }
    }


class TOTPVerifySetupRequest(BaseModel):
    """Request to verify TOTP code and complete setup."""

    secret: str = Field(..., description="TOTP secret being verified")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code from authenticator app")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "secret": "JBSWY3DPEHPK3PXP",
                    "otp_code": "123456"
                }
            ]
        }
    }


class TOTPVerifySetupResponse(BaseModel):
    """Response after successful TOTP setup verification."""

    status: str = Field(..., description="Setup status: 'success' or 'error'")
    message: str = Field(..., description="Status message")
    enrollment_id: Optional[int] = Field(None, description="MFA enrollment ID if successful")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "TOTP authenticator successfully configured",
                    "enrollment_id": 42
                }
            ]
        }
    }


class DuoEnrollmentRequest(BaseModel):
    """Request to send Duo enrollment SMS."""

    mfa_token: str = Field(..., description="Temporary MFA token from login response")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mfa_token": "temp_mfa_token_here"
                }
            ]
        }
    }


class DuoEnrollmentResponse(BaseModel):
    """Response for Duo enrollment SMS request."""

    success: bool = Field(..., description="Whether enrollment SMS was sent successfully")
    message: str = Field(..., description="User-friendly message")
    activation_url: Optional[str] = Field(None, description="Optional enrollment portal URL")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Enrollment instructions sent to +1XXX...X789. Please check your phone and follow the link to install Duo Mobile.",
                    "activation_url": "https://api-xxx.duosecurity.com/portal?code=abc123"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error summary")
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Invalid credentials",
                    "error_code": "AUTHENTICATION_FAILED",
                    "message": "The email or password you entered is incorrect"
                }
            ]
        }
    }

"""
Authentication schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
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
    mfa_method: Optional[str] = Field(None, description="MFA method required (e.g., 'duo_push')")

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

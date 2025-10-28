"""
Authentication API endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.logging import get_logger, request_id_ctx
from app.db.adapters import get_database_adapter
from app.db.models.user import User, Session as UserSession
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse, ErrorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password",
    responses={
        200: {"description": "Login successful", "model": LoginResponse},
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid credentials",
                        "error_code": "AUTHENTICATION_FAILED",
                        "message": "The email or password you entered is incorrect",
                        "request_id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        },
        423: {
            "description": "Account locked",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Account locked",
                        "error_code": "ACCOUNT_LOCKED",
                        "message": "Your account has been locked due to too many failed login attempts. Please try again after 2025-10-23 15:30:00 UTC",
                        "request_id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        },
    }
)
async def login(
    credentials: LoginRequest,
    request: Request
) -> LoginResponse:
    """
    Authenticate user with email and password.

    Args:
        credentials: Login credentials (email and password)
        request: FastAPI request object for IP and user agent

    Returns:
        LoginResponse with access token, refresh token, and user information

    Raises:
        HTTPException: If credentials are invalid or account is locked
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    # Get database session
    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            # Find user by email
            result = await session.execute(
                select(User).where(User.email == credentials.email)
            )
            user = result.scalar_one_or_none()

            # Check if user exists
            if not user:
                logger.warning(f"Login failed: User not found for email {credentials.email}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid credentials",
                        "error_code": "AUTHENTICATION_FAILED",
                        "message": "The email or password you entered is incorrect",
                        "request_id": request_id_ctx.get("")
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if account is locked
            if user.is_locked:
                logger.warning(f"Login failed: Account locked for user {user.id}")
                return JSONResponse(
                    status_code=status.HTTP_423_LOCKED,
                    content={
                        "detail": "Account locked",
                        "error_code": "ACCOUNT_LOCKED",
                        "message": f"Your account has been locked due to too many failed login attempts. Please try again after {user.locked_until.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        "request_id": request_id_ctx.get("")
                    }
                )

            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login failed: Account inactive for user {user.id}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Account inactive",
                        "error_code": "ACCOUNT_INACTIVE",
                        "message": "Your account has been deactivated. Please contact support for assistance",
                        "request_id": request_id_ctx.get("")
                    }
                )

            # Verify password
            if not user.password_hash or not verify_password(credentials.password, user.password_hash):
                # Increment failed login attempts
                user.failed_login_attempts += 1

                # Lock account if too many failed attempts
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=settings.account_lockout_duration)
                    logger.warning(f"Account locked for user {user.id} due to too many failed attempts")

                await session.commit()

                logger.warning(f"Login failed: Invalid password for user {user.id}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid credentials",
                        "error_code": "AUTHENTICATION_FAILED",
                        "message": "The email or password you entered is incorrect",
                        "request_id": request_id_ctx.get("")
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Successful login - reset failed attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()

            # Create JWT tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "username": user.username,
            }

            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)

            # Create session record
            session_record = UserSession(
                user_id=user.id,
                token_hash=access_token[:255],  # Store first 255 chars as identifier
                refresh_token_hash=refresh_token[:255],
                expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
                is_active=True,
                last_activity=datetime.utcnow(),
            )

            session.add(session_record)
            await session.commit()
            await session.refresh(user)

            logger.info(f"Login successful for user {user.id}")

            # Build response
            user_response = UserResponse.model_validate(user)

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=user_response,
                requires_mfa=False,  # MFA not implemented yet
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during login. Please try again later",
                    "request_id": request_id_ctx.get("")
                }
            )

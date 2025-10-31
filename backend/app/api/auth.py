"""
Authentication API endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import json
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.logging import get_logger, request_id_ctx
from app.core.duo_security import get_duo_service
from app.db.adapters import get_database_adapter
from app.db.models.user import User, Session as UserSession
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    ErrorResponse,
    MFAVerifyRequest,
    MFAStatusResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)

# Redis client for MFA token storage
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="The email or password you entered is incorrect"
                )

            # Check if account is locked
            if user.is_locked:
                logger.warning(f"Login failed: Account locked for user {user.id}")
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Your account has been locked due to too many failed login attempts. Please try again after {user.locked_until.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )

            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login failed: Account inactive for user {user.id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your account has been deactivated. Please contact support for assistance"
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="The email or password you entered is incorrect"
                )

            # Successful login - reset failed attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            await session.commit()

            # Check if MFA is enabled
            if settings.enable_mfa:
                logger.info(f"MFA enabled - initiating Duo Push for user {user.id}")

                try:
                    # Generate temporary MFA token
                    mfa_token = secrets.token_urlsafe(32)

                    # Store user info in Redis temporarily (5 minutes)
                    redis_client = await get_redis_client()
                    mfa_data = {
                        "user_id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "ip_address": request.client.host if request.client else None,
                        "user_agent": request.headers.get("User-Agent"),
                        "timestamp": datetime.utcnow().isoformat(),
                        "push_sent": False,
                    }
                    await redis_client.setex(
                        f"mfa_token:{mfa_token}",
                        300,  # 5 minutes expiry
                        json.dumps(mfa_data)
                    )

                    # Send Duo Push notification
                    duo_service = get_duo_service()
                    push_result = await duo_service.send_push_notification(
                        username=user.email,  # Use email as Duo username
                        push_type="Login Request",
                        push_info={
                            "Application": settings.app_name,
                            "IP Address": request.client.host if request.client else "Unknown"
                        }
                    )

                    # Update Redis with push result
                    mfa_data["push_sent"] = True
                    mfa_data["push_result"] = push_result.get("result")
                    mfa_data["push_status"] = push_result.get("status")
                    await redis_client.setex(
                        f"mfa_token:{mfa_token}",
                        300,
                        json.dumps(mfa_data)
                    )

                    logger.info(f"Duo Push sent to user {user.id}, result: {push_result.get('result')}")

                    # Return MFA required response
                    return LoginResponse(
                        token_type="bearer",
                        requires_mfa=True,
                        mfa_token=mfa_token,
                        mfa_method="duo_push"
                    )

                except Exception as e:
                    logger.error(f"Error during Duo Push for user {user.id}: {str(e)}", exc_info=True)
                    # Fall back to login without MFA on error
                    logger.warning(f"Falling back to login without MFA due to error")

            # MFA disabled or error occurred - proceed with normal login
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
                requires_mfa=False,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during login. Please try again later"
            )


@router.post(
    "/mfa/verify",
    response_model=MFAStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify MFA Push",
    description="Check Duo Push approval status and complete login"
)
async def verify_mfa(
    request: MFAVerifyRequest,
    http_request: Request
) -> MFAStatusResponse:
    """
    Check MFA push approval status and complete login if approved.

    Args:
        request: MFA verification request with mfa_token
        http_request: FastAPI request object

    Returns:
        MFAStatusResponse with approval status and tokens if approved
    """
    logger.info(f"MFA verification attempt with token: {request.mfa_token[:8]}...")

    try:
        # Get MFA data from Redis
        redis_client = await get_redis_client()
        mfa_data_json = await redis_client.get(f"mfa_token:{request.mfa_token}")

        if not mfa_data_json:
            logger.warning(f"Invalid or expired MFA token")
            return MFAStatusResponse(
                status="error",
                message="Invalid or expired MFA token. Please try logging in again."
            )

        mfa_data = json.loads(mfa_data_json)
        push_result = mfa_data.get("push_result")

        # Check push result
        if push_result == "allow":
            logger.info(f"Duo Push approved for user {mfa_data['user_id']}")

            # Delete MFA token from Redis
            await redis_client.delete(f"mfa_token:{request.mfa_token}")

            # Get database session and user
            db_adapter = get_database_adapter()
            async for db_session in db_adapter.get_session():
                try:
                    result = await db_session.execute(
                        select(User).where(User.id == mfa_data["user_id"])
                    )
                    user = result.scalar_one_or_none()

                    if not user:
                        return MFAStatusResponse(
                            status="error",
                            message="User not found"
                        )

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
                        token_hash=access_token[:255],
                        refresh_token_hash=refresh_token[:255],
                        expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
                        ip_address=mfa_data.get("ip_address"),
                        user_agent=mfa_data.get("user_agent"),
                        is_active=True,
                        last_activity=datetime.utcnow(),
                    )

                    db_session.add(session_record)
                    await db_session.commit()
                    await db_session.refresh(user)

                    logger.info(f"MFA verification successful for user {user.id}")

                    # Build response
                    user_response = UserResponse.model_validate(user)

                    return MFAStatusResponse(
                        status="approved",
                        message="Login successful",
                        access_token=access_token,
                        refresh_token=refresh_token,
                        user=user_response
                    )

                except Exception as e:
                    logger.error(f"Database error during MFA verification: {str(e)}", exc_info=True)
                    return MFAStatusResponse(
                        status="error",
                        message="An error occurred during verification"
                    )

        elif push_result == "deny":
            logger.warning(f"Duo Push denied for user {mfa_data['user_id']}")
            # Delete MFA token
            await redis_client.delete(f"mfa_token:{request.mfa_token}")
            return MFAStatusResponse(
                status="denied",
                message="Push notification denied. Please try logging in again."
            )

        elif push_result == "error":
            logger.error(f"Duo Push error for user {mfa_data['user_id']}")
            return MFAStatusResponse(
                status="error",
                message="An error occurred with the push notification"
            )

        else:
            # Still pending or no result yet
            return MFAStatusResponse(
                status="pending",
                message="Waiting for push approval. Please check your mobile device."
            )

    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}", exc_info=True)
        return MFAStatusResponse(
            status="error",
            message="An unexpected error occurred during verification"
        )

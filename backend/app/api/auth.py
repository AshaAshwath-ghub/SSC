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
    MFATriggerRequest,
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

                    # Check if user is enrolled in Duo first
                    duo_service = get_duo_service()

                    # Try email first, then fallback to username
                    user_status = await duo_service.check_user_status(user.email)
                    duo_identifier = user.email  # Track which identifier worked

                    # If email returns "enroll" but we expect they're enrolled, try username
                    if user_status.get('result') == 'enroll':
                        logger.info(f"Email {user.email} not found in Duo, trying username {user.username}")
                        user_status_by_username = await duo_service.check_user_status(user.username)
                        # Use username result if it's better than email result
                        if user_status_by_username.get('result') == 'auth':
                            logger.info(f"Found user in Duo by username: {user.username}")
                            user_status = user_status_by_username
                            duo_identifier = user.username  # Use username for push

                    duo_result = user_status.get('result')
                    duo_status = user_status.get('status')

                    logger.info(f"Duo enrollment check for user {user.id} ({user.email}): enrolled={user_status.get('enrolled')}, result={duo_result}, status={duo_status}")

                    # Store Duo enrollment status for later use
                    duo_enrolled = duo_result == "auth"

                    # Handle different Duo enrollment states
                    if duo_result == "deny":
                        # Only block if explicitly denied by policy
                        logger.warning(f"User {user.id} ({user.email}) denied by Duo policy - blocking login")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Your account has been denied access by security policy. Please contact your administrator."
                        )
                    elif duo_result == "allow":
                        # Duo bypass is enabled for this user - allow login without push
                        logger.info(f"User {user.id} ({user.email}) has Duo bypass enabled - skipping MFA")
                        # Fall through to normal login without MFA
                    elif duo_result == "enroll" or duo_result != "auth":
                        # User not enrolled - show MFA options but note they're not enrolled
                        logger.info(f"User {user.id} ({user.email}) not enrolled in Duo (result={duo_result}) - allowing login with MFA selection")
                        duo_enrolled = False
                        # Don't block - let them see MFA options

                    # Build list of available MFA methods
                    available_methods = []
                    devices = user_status.get('devices', [])

                    if duo_enrolled:
                        # User is fully enrolled in Duo - check device capabilities
                        # Check if user has devices that support push
                        has_push = any(
                            'push' in device.get('capabilities', [])
                            for device in devices
                        )
                        if has_push:
                            available_methods.append("duo_push")

                        # Check if user has phone for call
                        has_phone = any(
                            'phone' in device.get('capabilities', [])
                            for device in devices
                        )
                        if has_phone:
                            available_methods.append("duo_phone")
                    else:
                        # User not enrolled - still show Duo Push option
                        # But will check enrollment when they actually select it
                        available_methods.append("duo_push")

                    # SMS and Email OTP are always available as fallback methods
                    # These work independently of Duo device enrollment
                    available_methods.append("duo_sms")
                    available_methods.append("email_otp")

                    # Store MFA data with duo_identifier, enrollment status, and available methods
                    mfa_data["duo_identifier"] = duo_identifier
                    mfa_data["duo_enrolled"] = duo_enrolled
                    mfa_data["duo_result"] = duo_result
                    mfa_data["available_methods"] = available_methods
                    mfa_data["mfa_pending"] = True
                    await redis_client.setex(
                        f"mfa_token:{mfa_token}",
                        300,
                        json.dumps(mfa_data)
                    )

                    logger.info(f"MFA required for user {user.id}, duo_enrolled={duo_enrolled}, available methods: {available_methods}")

                    # Return MFA required response with available methods
                    return LoginResponse(
                        token_type="bearer",
                        requires_mfa=True,
                        mfa_token=mfa_token,
                        mfa_method="selection",  # Indicates user needs to select
                        available_mfa_methods=available_methods
                    )

                except HTTPException:
                    # Re-raise HTTP exceptions (like enrollment required)
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error during Duo Push for user {user.id}: {str(e)}", exc_info=True)
                    # For unexpected errors, raise a 503 Service Unavailable
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Multi-factor authentication service is temporarily unavailable. Please try again later or contact support."
                    )

            # MFA disabled - proceed with normal login
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
    "/mfa/trigger",
    status_code=status.HTTP_200_OK,
    summary="Trigger MFA Method",
    description="Trigger the selected MFA method (Duo Push, Phone Call, SMS, or Email OTP)"
)
async def trigger_mfa(
    request: MFATriggerRequest,
    http_request: Request
):
    """
    Trigger the selected MFA method for authentication.

    Args:
        request: MFA trigger request with mfa_token and method
        http_request: FastAPI request object

    Returns:
        Success message with instructions

    Raises:
        HTTPException: If token invalid or method not available
    """
    logger.info(f"MFA method trigger requested: method={request.method}, token={request.mfa_token[:8]}...")

    # Get MFA data from Redis
    redis_client = await get_redis_client()
    mfa_data_json = await redis_client.get(f"mfa_token:{request.mfa_token}")

    logger.info(f"MFA data from Redis: {mfa_data_json is not None}")

    if not mfa_data_json:
        logger.warning(f"Invalid or expired MFA token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired MFA token"
        )

    mfa_data = json.loads(mfa_data_json)
    available_methods = mfa_data.get("available_methods", [])

    # Check if requested method is available
    if request.method not in available_methods:
        logger.warning(f"Method {request.method} not available. Available: {available_methods}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MFA method '{request.method}' is not available for this user"
        )

    user_email = mfa_data.get("email")
    duo_identifier = mfa_data.get("duo_identifier")

    try:
        if request.method == "duo_push":
            # Check if user is enrolled in Duo first
            duo_enrolled = mfa_data.get("duo_enrolled", False)
            duo_result = mfa_data.get("duo_result")

            if not duo_enrolled:
                # User not enrolled in Duo - show friendly message
                logger.warning(f"User attempted Duo Push but is not enrolled. Result: {duo_result}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are not registered in Duo Security yet. Please contact your administrator to complete Duo enrollment (install Duo Mobile app and register your device) before using Duo Push authentication."
                )

            # Send Duo Push
            duo_service = get_duo_service()
            push_result = await duo_service.send_push_notification(
                username=duo_identifier,
                push_type="Login Request",
                push_info=None
            )

            if push_result.get("result") == "error":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to send push: {push_result.get('status_msg')}"
                )

            # Update MFA data with push result
            mfa_data["push_sent"] = True
            mfa_data["push_result"] = push_result.get("result")
            mfa_data["push_status"] = push_result.get("status")
            await redis_client.setex(
                f"mfa_token:{request.mfa_token}",
                300,
                json.dumps(mfa_data)
            )

            logger.info(f"Duo Push sent for token {request.mfa_token}")
            return {
                "status": "sent",
                "message": "Push notification sent to your device. Please approve it to continue.",
                "method": "duo_push"
            }

        elif request.method == "duo_phone":
            # Send Duo Phone Call
            duo_service = get_duo_service()
            phone_result = await duo_service.send_phone_call(username=duo_identifier)

            if phone_result.get("result") == "error":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to initiate call: {phone_result.get('status_msg')}"
                )

            mfa_data["phone_sent"] = True
            await redis_client.setex(
                f"mfa_token:{request.mfa_token}",
                300,
                json.dumps(mfa_data)
            )

            logger.info(f"Duo Phone call sent for token {request.mfa_token}")
            return {
                "status": "sent",
                "message": "You will receive a phone call shortly. Please answer and follow the instructions.",
                "method": "duo_phone"
            }

        elif request.method == "duo_sms":
            # Send Duo SMS
            duo_service = get_duo_service()
            sms_result = await duo_service.send_sms(username=duo_identifier)

            if sms_result.get("result") == "error":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to send SMS: {sms_result.get('status_msg')}"
                )

            mfa_data["sms_sent"] = True
            await redis_client.setex(
                f"mfa_token:{request.mfa_token}",
                300,
                json.dumps(mfa_data)
            )

            logger.info(f"Duo SMS sent for token {request.mfa_token}")
            return {
                "status": "sent",
                "message": "SMS sent to your registered phone number. Please enter the code you receive.",
                "method": "duo_sms"
            }

        elif request.method == "email_otp":
            # Generate and send email OTP
            otp_code = secrets.token_hex(3).upper()  # 6-character code

            # Store OTP in Redis
            mfa_data["email_otp"] = otp_code
            mfa_data["otp_sent"] = True
            await redis_client.setex(
                f"mfa_token:{request.mfa_token}",
                300,
                json.dumps(mfa_data)
            )

            # TODO: Send email with OTP code
            # For now, just log it (in production, integrate with email service)
            logger.info(f"Email OTP generated for {user_email}: {otp_code}")

            return {
                "status": "sent",
                "message": f"Verification code sent to {user_email}. Please check your email and enter the code.",
                "method": "email_otp",
                "otp": otp_code  # REMOVE THIS IN PRODUCTION! Only for testing
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown MFA method: {request.method}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering MFA method {request.method}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger MFA method"
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

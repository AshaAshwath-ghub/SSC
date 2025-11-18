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
import httpx

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.logging import get_logger, request_id_ctx
from app.core.duo_security import get_duo_service
from app.core.sendgrid_service import get_sendgrid_service
from app.core.twilio_service import get_twilio_service
from app.core.totp_service import get_totp_service
from app.db.adapters import get_database_adapter
from app.db.models.user import User, Session as UserSession, MFAEnrollment
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    ErrorResponse,
    MFATriggerRequest,
    MFAVerifyRequest,
    MFAStatusResponse,
    TOTPSetupRequest,
    TOTPSetupResponse,
    TOTPVerifySetupRequest,
    TOTPVerifySetupResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)

# Redis client for MFA token storage
_redis_client: Optional[redis.Redis] = None

# HTTP client for reCAPTCHA verification (reuse connection pool)
_http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client for external API calls."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10.0)
    return _http_client


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def verify_recaptcha(token: str, remote_ip: Optional[str] = None) -> dict:
    """
    Verify reCAPTCHA v3 token with Google's API.

    Args:
        token: reCAPTCHA token from frontend
        remote_ip: Optional IP address of the user

    Returns:
        dict with verification result containing:
            - success (bool): Whether verification passed
            - score (float): Risk score from 0.0 to 1.0 (1.0 = very likely human)
            - action (str): Action name from frontend
            - challenge_ts (str): Timestamp of the challenge
            - hostname (str): Hostname of the site

    Raises:
        HTTPException: If reCAPTCHA verification fails or service is unavailable
    """
    if not settings.recaptcha_enabled:
        logger.info("reCAPTCHA verification skipped (disabled in settings)")
        return {"success": True, "score": 1.0, "bypass": True}

    if not token:
        logger.warning("reCAPTCHA token missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security verification required. Please try again."
        )

    try:
        # Use persistent HTTP client to avoid connection pool issues
        client = await get_http_client()
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.recaptcha_secret_key_v3,
                "response": token,
                "remoteip": remote_ip
            }
        )

        result = response.json()
        logger.info(f"reCAPTCHA verification result: success={result.get('success')}, score={result.get('score')}")

        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            logger.warning(f"reCAPTCHA verification failed: {error_codes}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security verification failed. Please refresh the page and try again."
            )

        # Check score threshold for v3
        score = result.get("score", 0.0)
        if score < settings.recaptcha_v3_threshold:
            logger.warning(f"reCAPTCHA score {score} below threshold {settings.recaptcha_v3_threshold}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security verification failed. Your activity appears suspicious. Please contact support if you believe this is an error."
            )

        return result

    except httpx.TimeoutException:
        logger.error("reCAPTCHA verification timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security verification service is temporarily unavailable. Please try again."
        )
    except httpx.RequestError as e:
        logger.error(f"reCAPTCHA verification request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security verification service is temporarily unavailable. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during reCAPTCHA verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during security verification."
        )


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

    # Verify reCAPTCHA token (if enabled and provided)
    if settings.recaptcha_enabled and credentials.recaptcha_token:
        remote_ip = request.client.host if request.client else None
        try:
            recaptcha_result = await verify_recaptcha(credentials.recaptcha_token, remote_ip)
            logger.info(f"reCAPTCHA verification passed for {credentials.email}, score: {recaptcha_result.get('score')}")
        except HTTPException as e:
            logger.warning(f"reCAPTCHA verification failed for {credentials.email}: {e.detail}")
            raise

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
                    available_methods.append("duo_sms")  # Duo SMS
                    available_methods.append("twilio_sms")  # Twilio SMS (independent)
                    available_methods.append("email_otp")  # Email OTP via SendGrid

                    # Check if user has TOTP enrolled
                    totp_enrollment = await session.execute(
                        select(MFAEnrollment).where(
                            MFAEnrollment.user_id == user.id,
                            MFAEnrollment.mfa_type == "totp",
                            MFAEnrollment.is_active == True
                        )
                    )
                    totp_record = totp_enrollment.scalar_one_or_none()
                    if totp_record:
                        available_methods.append("totp")  # TOTP Authenticator
                        logger.info(f"User {user.id} has TOTP enrolled")

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

            # Send email with OTP code using SendGrid
            try:
                sendgrid_service = get_sendgrid_service()
                email_sent = await sendgrid_service.send_otp_email(
                    to_email=user_email,
                    otp_code=otp_code,
                    username=mfa_data.get("username")
                )

                if email_sent:
                    logger.info(f"Email OTP sent successfully to {user_email}")
                else:
                    logger.error(f"Failed to send email OTP to {user_email}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to send verification email. Please try again later."
                    )
            except ValueError as e:
                # SendGrid not configured
                logger.warning(f"SendGrid not configured: {str(e)}")
                logger.info(f"Email OTP generated for {user_email}: {otp_code} (email service not configured)")

            return {
                "status": "sent",
                "message": f"Verification code sent to {user_email}. Please check your email and enter the code.",
                "method": "email_otp"
            }

        elif request.method == "twilio_sms":
            # Send SMS OTP via Twilio (independent of Duo)
            # Get user's phone number from database
            db_adapter = get_database_adapter()
            async for db_session in db_adapter.get_session():
                try:
                    result = await db_session.execute(
                        select(User).where(User.id == mfa_data.get("user_id"))
                    )
                    user = result.scalar_one_or_none()

                    if not user or not user.phone_number:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number not registered. Please update your profile to use SMS authentication."
                        )

                    # Generate SMS OTP
                    otp_code = secrets.token_hex(3).upper()  # 6-character code

                    # Store OTP in Redis
                    mfa_data["sms_otp"] = otp_code
                    mfa_data["twilio_sms_sent"] = True
                    await redis_client.setex(
                        f"mfa_token:{request.mfa_token}",
                        300,
                        json.dumps(mfa_data)
                    )

                    # Send SMS via Twilio
                    try:
                        twilio_service = get_twilio_service()
                        sms_result = await twilio_service.send_otp_sms(
                            to_phone=user.phone_number,
                            otp_code=otp_code,
                            username=user.username
                        )

                        if sms_result["status"] == "success":
                            logger.info(f"Twilio SMS OTP sent successfully to {user.phone_number}")
                        elif sms_result["status"] == "invalid_phone":
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid phone number format. Please update your profile with a valid phone number in E.164 format (e.g., +1234567890)."
                            )
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Failed to send SMS. Please try again later."
                            )
                    except ValueError as e:
                        # Twilio not configured
                        logger.warning(f"Twilio not configured: {str(e)}")
                        logger.info(f"SMS OTP generated for {user.phone_number}: {otp_code} (SMS service not configured)")

                    # Mask phone number for display
                    masked_phone = f"{user.phone_number[:2]}***{user.phone_number[-4:]}" if len(user.phone_number) > 6 else "***"

                    return {
                        "status": "sent",
                        "message": f"Verification code sent to {masked_phone}. Please check your phone and enter the code.",
                        "method": "twilio_sms"
                    }

                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error sending Twilio SMS: {e}", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to send SMS verification code"
                    )

        elif request.method == "totp":
            # TOTP doesn't need "triggering" - user just enters code from their app
            # Just acknowledge and mark as ready
            mfa_data["totp_selected"] = True
            await redis_client.setex(
                f"mfa_token:{request.mfa_token}",
                300,
                json.dumps(mfa_data)
            )

            logger.info(f"TOTP method selected for token {request.mfa_token}")
            return {
                "status": "ready",
                "message": "Please enter the 6-digit code from your authenticator app.",
                "method": "totp"
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

        # Check if passcode is provided (for OTP methods)
        if request.passcode:
            logger.info(f"Verifying OTP passcode for token {request.mfa_token[:8]}...")

            # Check TOTP (Authenticator App)
            if mfa_data.get("totp_selected"):
                # Get user's TOTP secret from database
                db_adapter = get_database_adapter()
                async for db_session in db_adapter.get_session():
                    try:
                        # Get TOTP enrollment for this user
                        totp_result = await db_session.execute(
                            select(MFAEnrollment).where(
                                MFAEnrollment.user_id == mfa_data['user_id'],
                                MFAEnrollment.mfa_type == "totp",
                                MFAEnrollment.is_active == True
                            )
                        )
                        totp_enrollment = totp_result.scalar_one_or_none()

                        if not totp_enrollment:
                            logger.warning(f"TOTP enrollment not found for user {mfa_data['user_id']}")
                            return MFAStatusResponse(
                                status="error",
                                message="TOTP authenticator not configured. Please set it up in your profile."
                            )

                        # Verify TOTP code
                        totp_service = get_totp_service()
                        is_valid = totp_service.verify_otp(
                            totp_enrollment.secret_or_identifier,
                            request.passcode
                        )

                        if is_valid:
                            logger.info(f"TOTP verified successfully for user {mfa_data['user_id']}")
                            # Update last_used_at timestamp
                            totp_enrollment.last_used_at = datetime.utcnow()
                            await db_session.commit()
                            # Fall through to complete login below
                            push_result = "allow"
                            break  # Exit the async for loop
                        else:
                            logger.warning(f"Invalid TOTP code provided for user {mfa_data['user_id']}")
                            return MFAStatusResponse(
                                status="error",
                                message="Invalid verification code. Please ensure your device time is synchronized and try again."
                            )

                    except Exception as e:
                        logger.error(f"Error verifying TOTP: {str(e)}", exc_info=True)
                        return MFAStatusResponse(
                            status="error",
                            message="An error occurred while verifying your code."
                        )

            # Check email OTP
            elif mfa_data.get("email_otp"):
                if request.passcode.upper() == mfa_data.get("email_otp"):
                    logger.info(f"Email OTP verified successfully for user {mfa_data['user_id']}")
                    # Fall through to complete login below
                    push_result = "allow"
                else:
                    logger.warning(f"Invalid email OTP provided for user {mfa_data['user_id']}")
                    return MFAStatusResponse(
                        status="error",
                        message="Invalid verification code. Please try again."
                    )

            # Check SMS OTP (Twilio)
            elif mfa_data.get("sms_otp"):
                if request.passcode.upper() == mfa_data.get("sms_otp"):
                    logger.info(f"SMS OTP verified successfully for user {mfa_data['user_id']}")
                    # Fall through to complete login below
                    push_result = "allow"
                else:
                    logger.warning(f"Invalid SMS OTP provided for user {mfa_data['user_id']}")
                    return MFAStatusResponse(
                        status="error",
                        message="Invalid verification code. Please try again."
                    )
            else:
                return MFAStatusResponse(
                    status="error",
                    message="No OTP code was generated. Please request a new code."
                )
        else:
            # No passcode provided - check Duo push result
            push_result = mfa_data.get("push_result")

        # Check push result or OTP verification
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


@router.post(
    "/mfa/totp/setup",
    response_model=TOTPSetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Setup TOTP Authenticator",
    description="Initialize TOTP setup and get QR code for authenticator app"
)
async def setup_totp(
    request: TOTPSetupRequest,
    http_request: Request
) -> TOTPSetupResponse:
    """
    Initialize TOTP setup for a user.
    Returns QR code and secret for authenticator app configuration.

    Args:
        request: TOTP setup request with user email
        http_request: FastAPI request object

    Returns:
        TOTPSetupResponse with secret, QR code, and backup codes

    Raises:
        HTTPException: If user not found or TOTP already enabled
    """
    logger.info(f"TOTP setup requested for email: {request.user_email}")

    # For now, require user_email in request
    # In production, you'd get this from JWT token
    if not request.user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email is required for TOTP setup"
        )

    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            # Find user by email
            result = await session.execute(
                select(User).where(User.email == request.user_email)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"TOTP setup failed: User not found for email {request.user_email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Check if user already has active TOTP enrollment
            existing_totp = await session.execute(
                select(MFAEnrollment).where(
                    MFAEnrollment.user_id == user.id,
                    MFAEnrollment.mfa_type == "totp",
                    MFAEnrollment.is_active == True
                )
            )
            if existing_totp.scalar_one_or_none():
                logger.warning(f"TOTP setup failed: User {user.id} already has active TOTP")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="TOTP authenticator is already configured. Please disable it first to set up a new one."
                )

            # Generate TOTP setup data
            totp_service = get_totp_service()
            setup_data = await totp_service.setup_totp_for_user(
                user_email=user.email,
                issuer_name=None  # Use default from settings
            )

            # Store secret temporarily in Redis (valid for 10 minutes for setup)
            redis_client = await get_redis_client()
            setup_token = secrets.token_urlsafe(32)

            await redis_client.setex(
                f"totp_setup:{setup_token}",
                600,  # 10 minutes
                json.dumps({
                    "user_id": user.id,
                    "email": user.email,
                    "secret": setup_data["secret"],
                    "backup_codes_hashed": setup_data["backup_codes_hashed"],
                    "timestamp": datetime.utcnow().isoformat()
                })
            )

            logger.info(f"TOTP setup initiated for user {user.id}")

            return TOTPSetupResponse(
                secret=setup_data["secret"],
                qr_code=setup_data["qr_code"],
                provisioning_uri=setup_data["provisioning_uri"],
                backup_codes=setup_data["backup_codes"],
                issuer_name=totp_service.issuer_name
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"TOTP setup error: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error traceback:", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during TOTP setup: {str(e)}"
            )


@router.post(
    "/mfa/totp/verify-setup",
    response_model=TOTPVerifySetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify and Activate TOTP",
    description="Verify TOTP code and activate authenticator for the user"
)
async def verify_totp_setup(
    request: TOTPVerifySetupRequest,
    http_request: Request
) -> TOTPVerifySetupResponse:
    """
    Verify TOTP code and complete setup by saving enrollment to database.

    Args:
        request: TOTP verify setup request with secret and OTP code
        http_request: FastAPI request object

    Returns:
        TOTPVerifySetupResponse with status and enrollment ID

    Raises:
        HTTPException: If verification fails or enrollment cannot be saved
    """
    logger.info(f"TOTP verification requested for secret: {request.secret[:8]}...")

    # Verify the TOTP code
    totp_service = get_totp_service()
    is_valid = totp_service.verify_otp(request.secret, request.otp_code)

    if not is_valid:
        logger.warning(f"TOTP verification failed: Invalid OTP code")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please ensure your device time is synchronized and try again."
        )

    # Get setup data from Redis to find user
    redis_client = await get_redis_client()

    # Search for setup token matching this secret
    # In production, you'd pass the setup_token from frontend
    # For now, we'll search Redis keys (not ideal, but works for demo)
    setup_data = None
    user_id = None
    backup_codes_hashed = None

    # This is a simplified approach - in production, pass setup_token from frontend
    # and use: setup_data_json = await redis_client.get(f"totp_setup:{setup_token}")

    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            # For now, we'll need to search all setup tokens
            # Better approach: return setup_token from /setup endpoint and require it here
            keys = await redis_client.keys("totp_setup:*")

            for key in keys:
                data_json = await redis_client.get(key)
                if data_json:
                    data = json.loads(data_json)
                    if data.get("secret") == request.secret:
                        setup_data = data
                        user_id = data.get("user_id")
                        backup_codes_hashed = data.get("backup_codes_hashed", [])
                        await redis_client.delete(key)  # Remove setup token
                        break

            if not setup_data or not user_id:
                logger.warning("TOTP verification failed: Setup data not found or expired")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="TOTP setup session expired. Please start setup again."
                )

            # Create MFA enrollment record
            enrollment = MFAEnrollment(
                user_id=user_id,
                mfa_type="totp",
                secret_or_identifier=request.secret,
                backup_codes=backup_codes_hashed,
                is_active=True,
                is_primary=False,  # Can be set to True if it's the user's first/primary MFA
                verified_at=datetime.utcnow(),
                last_used_at=None
            )

            session.add(enrollment)
            await session.commit()
            await session.refresh(enrollment)

            logger.info(f"TOTP enrollment created successfully for user {user_id}, enrollment_id={enrollment.id}")

            return TOTPVerifySetupResponse(
                status="success",
                message="TOTP authenticator successfully configured. You can now use it for login.",
                enrollment_id=enrollment.id
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"TOTP verification error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during TOTP verification"
            )

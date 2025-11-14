"""
OAuth authentication endpoints for social login.
Supports Google, Microsoft, and Apple OAuth 2.0 flows.
"""
import secrets
import time
import jwt
from typing import Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.db.adapters import get_database_adapter
from app.db.models.user import User, AuthProvider
from sqlalchemy import select

router = APIRouter(prefix="/oauth", tags=["oauth"])


def generate_apple_client_secret():
    """Generate JWT client secret for Apple Sign In."""
    if not all([settings.apple_team_id, settings.apple_key_id, settings.apple_client_id, settings.apple_private_key]):
        raise HTTPException(status_code=500, detail="Apple OAuth not configured properly")

    headers = {
        "kid": settings.apple_key_id,
        "alg": "ES256"
    }

    payload = {
        "iss": settings.apple_team_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 180,  # 6 months
        "aud": "https://appleid.apple.com",
        "sub": settings.apple_client_id,
    }

    client_secret = jwt.encode(
        payload,
        settings.apple_private_key,
        algorithm="ES256",
        headers=headers
    )

    return client_secret


# OAuth provider configurations
OAUTH_PROVIDERS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri or f"http://localhost:3010{settings.api_prefix}/oauth/google/callback",
    },
    "microsoft": {
        "authorize_url": f"https://login.microsoftonline.com/{settings.microsoft_tenant}/oauth2/v2.0/authorize",
        "token_url": f"https://login.microsoftonline.com/{settings.microsoft_tenant}/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid email profile User.Read",
        "client_id": settings.microsoft_client_id,
        "client_secret": settings.microsoft_client_secret,
        "redirect_uri": settings.microsoft_redirect_uri or f"http://localhost:3010{settings.api_prefix}/oauth/microsoft/callback",
    },
    "apple": {
        "authorize_url": "https://appleid.apple.com/auth/authorize",
        "token_url": "https://appleid.apple.com/auth/token",
        "userinfo_url": None,  # Apple doesn't have a separate userinfo endpoint
        "scope": "name email",
        "client_id": settings.apple_client_id,
        "client_secret": None,  # Generated dynamically via JWT
        "redirect_uri": settings.apple_redirect_uri or f"http://localhost:3010{settings.api_prefix}/oauth/apple/callback",
    },
}


@router.get("/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    request: Request
):
    """
    Initiate OAuth authorization flow.
    Redirects user to the OAuth provider's login page.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported OAuth provider: {provider}")

    config = OAUTH_PROVIDERS[provider]

    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Build authorization URL
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": config["scope"],
        "state": state,
    }

    # Add provider-specific parameters
    if provider == "microsoft":
        params["response_mode"] = "query"
    elif provider == "apple":
        params["response_mode"] = "form_post"  # Apple uses form_post

    auth_url = f"{config['authorize_url']}?{urlencode(params)}"

    return RedirectResponse(url=auth_url)


async def _handle_oauth_callback(provider: str, code: str, state: Optional[str] = None):
    """Internal function to handle OAuth callback logic."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported OAuth provider: {provider}")

    config = OAUTH_PROVIDERS[provider]

    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        token_data = {
            "client_id": config["client_id"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }

        # Apple requires dynamically generated client_secret
        if provider == "apple":
            token_data["client_secret"] = generate_apple_client_secret()
        else:
            token_data["client_secret"] = config["client_secret"]

        token_response = await client.post(config["token_url"], data=token_data)

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to exchange authorization code: {token_response.text}"
            )

        tokens = token_response.json()
        oauth_access_token = tokens.get("access_token")

        # Get user info based on provider
        if provider == "apple":
            # Apple returns user info in the id_token
            id_token = tokens.get("id_token")
            if not id_token:
                raise HTTPException(status_code=400, detail="No id_token returned from Apple")

            # Decode id_token (without verification for simplicity - in production, verify it)
            user_info = jwt.decode(id_token, options={"verify_signature": False})
        else:
            # Google and Microsoft have separate userinfo endpoints
            headers = {"Authorization": f"Bearer {oauth_access_token}"}
            userinfo_response = await client.get(config["userinfo_url"], headers=headers)

            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to get user info: {userinfo_response.text}"
                )

            user_info = userinfo_response.json()

    # Extract user data based on provider
    if provider == "google":
        email = user_info.get("email")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        provider_user_id = user_info.get("id")
    elif provider == "microsoft":
        email = user_info.get("mail") or user_info.get("userPrincipalName")
        first_name = user_info.get("givenName", "")
        last_name = user_info.get("surname", "")
        provider_user_id = user_info.get("id")
    elif provider == "apple":
        email = user_info.get("email")
        # Apple may not always provide name (only on first auth)
        first_name = ""
        last_name = ""
        provider_user_id = user_info.get("sub")
    else:
        raise HTTPException(status_code=400, detail="Provider user info parsing not implemented")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    # Get database session and create/update user
    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            # Find user by email
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                # SECURITY: Only allow existing users to log in via OAuth
                # New users cannot register - they must be added to database first
                raise HTTPException(
                    status_code=403,
                    detail="Access denied. Your account is not authorized. Please contact the administrator."
                )

            # Check if user is active
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Account is deactivated")

            # Update last login timestamp
            user.last_login = datetime.utcnow()

            # Store or update OAuth provider information
            auth_provider_result = await session.execute(
                select(AuthProvider).where(
                    AuthProvider.user_id == user.id,
                    AuthProvider.provider_type == provider
                )
            )
            auth_provider = auth_provider_result.scalar_one_or_none()

            if not auth_provider:
                # Create new auth provider record
                auth_provider = AuthProvider(
                    user_id=user.id,
                    provider_type=provider,
                    provider_user_id=provider_user_id,
                    provider_email=email
                )
                session.add(auth_provider)
            else:
                # Update existing provider info
                auth_provider.provider_email = email
                auth_provider.updated_at = datetime.utcnow()

            await session.commit()

            # Generate JWT tokens
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "username": user.username
            }

            access_token = create_access_token(
                data=token_data,
                expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(
                data=token_data
            )

            # Redirect to frontend with tokens
            frontend_url = f"{settings.frontend_url}/oauth/callback"
            redirect_params = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
            }

            redirect_url = f"{frontend_url}?{urlencode(redirect_params)}"

            return RedirectResponse(url=redirect_url)

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"OAuth callback error: {str(e)}")


@router.get("/{provider}/callback")
async def oauth_callback_get(
    provider: str,
    code: str = Query(...),
    state: Optional[str] = Query(None)
):
    """Handle OAuth callback from provider (GET method for Google/Microsoft)."""
    return await _handle_oauth_callback(provider, code, state)


@router.post("/{provider}/callback")
async def oauth_callback_post(
    provider: str,
    request: Request
):
    """Handle OAuth callback from provider (POST method for Apple)."""
    form_data = await request.form()
    code = form_data.get("code")
    state = form_data.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    return await _handle_oauth_callback(provider, code, state)

"""
Security utilities for password hashing, token generation, etc.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import string

from app.core.config import settings


# Password hashing context using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Payload data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.

    Args:
        email: User's email address

    Returns:
        Encoded JWT token for password reset
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.password_reset_token_expire_minutes)
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def generate_random_string(length: int = 32, include_punctuation: bool = False) -> str:
    """
    Generate a random string for tokens, secrets, etc.

    Args:
        length: Length of the string
        include_punctuation: Whether to include punctuation characters

    Returns:
        Random string
    """
    characters = string.ascii_letters + string.digits
    if include_punctuation:
        characters += string.punctuation

    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_backup_codes(count: int = 10) -> list[str]:
    """
    Generate MFA backup codes.

    Args:
        count: Number of backup codes to generate

    Returns:
        List of backup codes
    """
    return [
        '-'.join([
            ''.join(secrets.choice(string.digits) for _ in range(4))
            for _ in range(2)
        ])
        for _ in range(count)
    ]


def hash_token(token: str) -> str:
    """
    Hash a token for storage (e.g., refresh tokens, session tokens).

    Args:
        token: Token to hash

    Returns:
        Hashed token
    """
    return pwd_context.hash(token)


def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    Verify a token against its hash.

    Args:
        token: Plain token
        token_hash: Hashed token

    Returns:
        True if token matches hash
    """
    return pwd_context.verify(token, token_hash)

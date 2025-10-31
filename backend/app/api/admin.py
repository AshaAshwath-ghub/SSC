"""
Admin API endpoints for user management.
"""
import secrets
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.core.logging import get_logger
from app.db.adapters import get_database_adapter
from app.db.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = get_logger(__name__)


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    password: Optional[str] = Field(None, min_length=8, description="Password (optional, auto-generated if not provided)")
    is_active: bool = Field(True, description="Is the user account active?")
    is_verified: bool = Field(True, description="Is the email verified?")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePass123!",
                "is_active": True,
                "is_verified": True
            }
        }


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "message": "User created successfully. They can now log in via OAuth."
            }
        }


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account. This user will be authorized to log in via OAuth (Google, Microsoft, Apple).",
    responses={
        201: {"description": "User created successfully", "model": UserResponse},
        400: {
            "description": "Bad request - Email or username already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with this email already exists"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_user(user_data: CreateUserRequest) -> UserResponse:
    """
    Create a new user account.

    This endpoint allows you to add authorized users to the database.
    Once added, they can log in using OAuth (Google, Microsoft, or Apple)
    if their OAuth email matches the email in the database.

    Args:
        user_data: User creation data

    Returns:
        UserResponse with created user information

    Raises:
        HTTPException: If email or username already exists
    """
    logger.info(f"Creating new user with email: {user_data.email}")

    # Get database session
    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            # Check if email already exists
            result = await session.execute(
                select(User).where(User.email == user_data.email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.warning(f"User creation failed: Email {user_data.email} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{user_data.email}' already exists"
                )

            # Check if username already exists
            result = await session.execute(
                select(User).where(User.username == user_data.username)
            )
            existing_username = result.scalar_one_or_none()

            if existing_username:
                logger.warning(f"User creation failed: Username {user_data.username} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{user_data.username}' already exists"
                )

            # Generate password if not provided
            password = user_data.password if user_data.password else secrets.token_urlsafe(32)

            # Create new user
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                password_hash=hash_password(password),
                is_active=user_data.is_active,
                is_verified=user_data.is_verified
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            logger.info(f"User created successfully: {new_user.email} (ID: {new_user.id})")

            return UserResponse(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                is_active=new_user.is_active,
                is_verified=new_user.is_verified,
                message="User created successfully. They can now log in via OAuth."
            )

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
        finally:
            break


@router.get(
    "/users",
    summary="List all users",
    description="Get a list of all users in the database",
    responses={
        200: {
            "description": "List of users",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "johndoe",
                            "first_name": "John",
                            "last_name": "Doe",
                            "is_active": True,
                            "is_verified": True
                        }
                    ]
                }
            }
        }
    }
)
async def list_users():
    """
    Get a list of all users in the database.

    Returns:
        List of all users with their basic information
    """
    logger.info("Fetching all users")

    db_adapter = get_database_adapter()
    async for session in db_adapter.get_session():
        try:
            result = await session.execute(
                select(
                    User.id,
                    User.email,
                    User.username,
                    User.first_name,
                    User.last_name,
                    User.is_active,
                    User.is_verified
                )
            )
            users = result.all()

            user_list = [
                {
                    "id": user[0],
                    "email": user[1],
                    "username": user[2],
                    "first_name": user[3],
                    "last_name": user[4],
                    "is_active": user[5],
                    "is_verified": user[6]
                }
                for user in users
            ]

            logger.info(f"Fetched {len(user_list)} users")
            return user_list

        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch users: {str(e)}"
            )
        finally:
            break

"""Authentication controller for user management."""

import json
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.responses import AppJSONResponse
from app.models.user import SubscriptionInfo, Token, User, UserCreate
from app.services.auth import auth_service

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth_service.get_current_user(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role=user.role,
        subscription_plan=user.subscription_plan,
        searches_used_this_month=user.searches_used_this_month,
        searches_limit=user.searches_limit,
        subscription_expires_at=user.subscription_expires_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", response_model=User)
async def register(
    user_create: UserCreate, db: AsyncSession = Depends(get_db)
) -> AppJSONResponse:
    """Register a new user account."""
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_create.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = await auth_service.create_user(user_create, db)

    return AppJSONResponse(
        data=User.model_validate(user).model_dump(),
        message="User registered successfully",
        status_code=201,
    )


@router.post("/login", response_model=Token)
async def login(
    login: LoginRequest, db: AsyncSession = Depends(get_db)
) -> AppJSONResponse:
    email = login.email
    password = login.password
    # Authenticate user
    user = await auth_service.authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    # Create access token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    return AppJSONResponse(
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
        ).model_dump(),
        message="Login successful",
        status_code=200,
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> AppJSONResponse:
    """Get current user information."""
    return AppJSONResponse(
        data=json.loads(current_user.model_dump_json()),
        message="User information retrieved successfully",
        status_code=200,
    )


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription_info(
    current_user: User = Depends(get_current_user),
) -> AppJSONResponse:
    """Get current user's subscription information."""
    # Calculate days remaining
    days_remaining = None
    if current_user.subscription_expires_at:
        days_remaining = (current_user.subscription_expires_at - datetime.utcnow()).days

    subscription_info = SubscriptionInfo(
        plan=current_user.subscription_plan,
        searches_used=current_user.searches_used_this_month,
        searches_limit=current_user.searches_limit,
        expires_at=current_user.subscription_expires_at,
        is_active=current_user.subscription_expires_at is None
        or current_user.subscription_expires_at > datetime.utcnow(),
        days_remaining=days_remaining,
    )

    return AppJSONResponse(
        data=subscription_info.model_dump(),
        message="Subscription information retrieved successfully",
        status_code=200,
    )


@router.post("/logout")
async def logout() -> AppJSONResponse:
    """Logout user (client should discard token)."""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return success (client handles token disposal)

    return AppJSONResponse(
        data={"message": "Logged out successfully"},
        message="Logout successful",
        status_code=200,
    )


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> AppJSONResponse:
    """Refresh access token."""
    # Create new access token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value,
        },
        expires_delta=access_token_expires,
    )

    return AppJSONResponse(
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
        ).model_dump(),
        message="Token refreshed successfully",
        status_code=200,
    )

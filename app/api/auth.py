"""Authentication endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import authenticate_user, create_access_token, create_user, get_current_user
from app.core.database import get_db
from app.models import SubscriptionInfo, Token, User, UserCreate
from app.responses import create_response

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


@router.post("/register", response_model=User)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    try:
        user = await create_user(user_create, db)
        user_response = User.model_validate(user, from_attributes=True)
        return create_response(
            data=user_response.model_dump(),
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    user = await authenticate_user(login_request.email, login_request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)  # From settings
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return create_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes in seconds
        },
        message="Login successful"
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return create_response(
        data=current_user.model_dump(),
        message="User information retrieved successfully"
    )


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription information."""
    subscription_info = SubscriptionInfo(
        plan=current_user.subscription_plan,
        searches_used=current_user.searches_used_this_month,
        searches_limit=current_user.searches_limit,
        expires_at=current_user.subscription_expires_at
    )
    
    return create_response(
        data=subscription_info.model_dump(),
        message="Subscription information retrieved successfully"
    )


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)."""
    return create_response(
        data={"message": "Logged out successfully"},
        message="Logout successful"
    )


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token."""
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return create_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800
        },
        message="Token refreshed successfully"
    )
"""User models for authentication and subscription management."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class SubscriptionPlan(str, Enum):
    """Available subscription plans."""

    FREE = "free"
    PRO = "pro"
    ACADEMIC = "academic"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    """User roles for access control."""

    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    is_active: bool = Field(default=True, description="Whether user account is active")


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Model for updating user information."""

    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserInDB(UserBase):
    """User model as stored in database."""

    id: int = Field(..., description="User ID")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE, description="Current subscription plan")
    searches_used_this_month: int = Field(default=0, description="Number of searches used this month")
    searches_limit: int = Field(default=10, description="Monthly search limit")
    subscription_expires_at: datetime | None = Field(default=None, description="Subscription expiry date")
    stripe_customer_id: str | None = Field(default=None, description="Stripe customer ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update date")


class User(UserBase):
    """User model for API responses."""

    id: int
    role: UserRole
    subscription_plan: SubscriptionPlan
    searches_used_this_month: int
    searches_limit: int
    subscription_expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")


class TokenData(BaseModel):
    """Token payload data."""

    user_id: int | None = None
    email: str | None = None
    role: str | None = None


class SubscriptionInfo(BaseModel):
    """Subscription information model."""

    plan: SubscriptionPlan
    searches_used: int
    searches_limit: int
    expires_at: datetime | None
    is_active: bool = Field(..., description="Whether subscription is active")
    days_remaining: int | None = Field(None, description="Days until subscription expires")


class PasswordReset(BaseModel):
    """Password reset request model."""

    email: EmailStr = Field(..., description="Email for password reset")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


def get_subscription_limits(plan: SubscriptionPlan) -> dict:
    """Get search limits for each subscription plan."""
    limits = {
        SubscriptionPlan.FREE: {
            "searches_limit": 10,
            "price": 0,
            "features": ["Basic research", "Citations"],
        },
        SubscriptionPlan.PRO: {
            "searches_limit": 100,
            "price": 19,
            "features": ["Advanced research", "Exports", "Analytics"],
        },
        SubscriptionPlan.ACADEMIC: {
            "searches_limit": 500,
            "price": 29,
            "features": ["Academic tools", "Collaboration", "Priority support"],
        },
        SubscriptionPlan.ENTERPRISE: {
            "searches_limit": -1,  # Unlimited
            "price": 99,
            "features": ["API access", "White-label", "Custom integrations"],
        },
    }
    return limits.get(plan, limits[SubscriptionPlan.FREE])


def can_user_search(user: UserInDB) -> tuple[bool, str]:
    """Check if user can perform a search."""
    if not user.is_active:
        return False, "Account is deactivated"

    if user.subscription_plan == SubscriptionPlan.ENTERPRISE:
        return True, "Unlimited searches"

    if user.searches_used_this_month >= user.searches_limit:
        return False, "Monthly search limit exceeded"

    if user.subscription_expires_at and user.subscription_expires_at < datetime.utcnow():
        return False, "Subscription has expired"

    return True, "Search allowed"

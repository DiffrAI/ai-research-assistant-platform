"""Unified models for the application."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func

from app.core.database import Base


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"


class SubscriptionPlan(str, Enum):
    """Subscription plan enumeration."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


def get_subscription_limits(plan: SubscriptionPlan) -> dict:
    """Get subscription limits for a plan."""
    limits = {
        SubscriptionPlan.FREE: {
            "searches_limit": 10,
            "price": 0,
            "features": ["Basic search", "Limited results"],
        },
        SubscriptionPlan.BASIC: {
            "searches_limit": 100,
            "price": 9,
            "features": ["Enhanced search", "Export results", "Priority support"],
        },
        SubscriptionPlan.PRO: {
            "searches_limit": 500,
            "price": 29,
            "features": ["Advanced search", "Unlimited exports", "API access"],
        },
        SubscriptionPlan.ENTERPRISE: {
            "searches_limit": -1,
            "price": 99,
            "features": [
                "Unlimited everything",
                "Custom integrations",
                "Dedicated support",
            ],
        },
    }
    return limits.get(plan, limits[SubscriptionPlan.FREE])


# Pydantic Models
class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8)


class User(UserBase):
    """User response model."""

    id: int
    role: UserRole
    subscription_plan: SubscriptionPlan
    searches_used_this_month: int
    searches_limit: int
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model."""

    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class SubscriptionInfo(BaseModel):
    """Subscription information model."""

    plan: SubscriptionPlan
    searches_used: int
    searches_limit: int
    expires_at: Optional[datetime] = None


# SQLAlchemy Models
class UserDB(Base):
    """SQLAlchemy User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role: UserRole = Column(SQLEnum(UserRole), default=UserRole.USER)  # type: ignore
    subscription_plan: SubscriptionPlan = Column(
        SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE
    )  # type: ignore
    searches_used_this_month = Column(Integer, default=0)
    searches_limit = Column(Integer, default=10)
    subscription_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

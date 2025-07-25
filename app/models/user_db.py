"""SQLAlchemy User model for database."""

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.user import SubscriptionPlan, UserRole


class User(Base):  # type: ignore
    """User model for database storage."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)  # type: ignore
    subscription_plan = Column(
        Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False
    )  # type: ignore
    is_active = Column(Boolean, default=True, nullable=False)
    searches_used_this_month = Column(Integer, default=0, nullable=False)
    searches_limit = Column(Integer, default=10, nullable=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
        )

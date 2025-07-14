"""Authentication service for user management."""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.models.user import TokenData, UserCreate, UserInDB
from app.models.user_db import User as UserDB

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication and user management."""

    def __init__(self):  # type: ignore
        """Initialize the auth service."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bool(pwd_context.verify(plain_password, hashed_password))

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return str(pwd_context.hash(password))

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        return str(jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm))

    def verify_token(self, token: str) -> TokenData | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str: str | None = payload.get("sub")
            email: str | None = payload.get("email")
            role: str | None = payload.get("role")

            if user_id_str is None:
                return None

            # Convert string user_id to int
            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError):
                return None

            return TokenData(user_id=user_id, email=email, role=role)
        except JWTError:
            return None

    async def authenticate_user(
        self, email: str, password: str, db: AsyncSession
    ) -> UserInDB | None:
        """Authenticate a user with email and password."""
        # Get user from database
        user = await self.get_user_by_email(email, db)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    async def create_user(self, user_create: UserCreate, db: AsyncSession) -> UserInDB:
        """Create a new user account."""
        from app.models.user import SubscriptionPlan, UserRole

        # Check if user already exists
        existing_user = await self.get_user_by_email(user_create.email, db)
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user in database
        db_user = UserDB(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=self.get_password_hash(user_create.password),
            role=UserRole.USER,
            subscription_plan=SubscriptionPlan.FREE,
            is_active=True,
            searches_used_this_month=0,
            searches_limit=10,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Convert to UserInDB
        return UserInDB.model_validate(db_user, from_attributes=True)

    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> UserInDB | None:
        """Get a user by ID."""
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one_or_none()

        if db_user:
            return UserInDB.model_validate(db_user, from_attributes=True)
        return None

    async def get_user_by_email(self, email: str, db: AsyncSession) -> UserInDB | None:
        """Get a user by email."""
        result = await db.execute(select(UserDB).where(UserDB.email == email))
        db_user = result.scalar_one_or_none()

        if db_user:
            return UserInDB.model_validate(db_user, from_attributes=True)
        return None

    async def increment_user_searches(self, user_id: int, db: AsyncSession) -> bool:
        """Increment user's search count for the current month."""
        try:
            result = await db.execute(select(UserDB).where(UserDB.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                object.__setattr__(
                    user,
                    "searches_used_this_month",
                    int(getattr(user, "searches_used_this_month", 0)) + 1,
                )
                await db.commit()
                logger.info(f"Incremented searches for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error incrementing searches for user {user_id}: {e}")
            await db.rollback()
        return False

    async def get_current_user(self, token: str, db: AsyncSession) -> UserInDB | None:
        """Get current user from JWT token."""
        token_data = self.verify_token(token)
        if token_data is None or token_data.email is None:
            return None

        # Get user from database
        return await self.get_user_by_email(token_data.email, db)


# Create global auth service instance
auth_service = AuthService()

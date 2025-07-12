"""Authentication service for user management."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from app import settings
from app.models.user import UserInDB, TokenData, UserCreate, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication and user management."""

    def __init__(self):
        """Initialize the auth service."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: Optional[int] = payload.get("sub")
            email: Optional[str] = payload.get("email")
            role: Optional[str] = payload.get("role")
            
            if user_id is None:
                return None
            
            return TokenData(user_id=user_id, email=email, role=role)
        except JWTError:
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password."""
        # TODO: Implement actual database lookup
        # For demo purposes, return a mock user
        if email == "demo@example.com" and password == "password123":
            return UserInDB(
                id=1,
                email=email,
                full_name="Demo User",
                hashed_password=self.get_password_hash(password),
                is_active=True,
                searches_used_this_month=5,
                searches_limit=10,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        return None

    async def create_user(self, user_create: UserCreate) -> UserInDB:
        """Create a new user account."""
        # TODO: Implement actual database creation
        # For demo purposes, return a mock user
        return UserInDB(
            id=1,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=self.get_password_hash(user_create.password),
            is_active=True,
            searches_used_this_month=0,
            searches_limit=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Get a user by ID."""
        # TODO: Implement actual database lookup
        # For demo purposes, return a mock user
        return UserInDB(
            id=user_id,
            email="demo@example.com",
            full_name="Demo User",
            hashed_password="hashed_password",
            is_active=True,
            searches_used_this_month=5,
            searches_limit=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email."""
        # TODO: Implement actual database lookup
        # For demo purposes, return a mock user
        return UserInDB(
            id=1,
            email=email,
            full_name="Demo User",
            hashed_password="hashed_password",
            is_active=True,
            searches_used_this_month=5,
            searches_limit=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def increment_user_searches(self, user_id: int) -> bool:
        """Increment user's search count for the current month."""
        # TODO: Implement actual database update
        logger.info(f"Incrementing searches for user {user_id}")
        return True

    def get_current_user(self, token: str) -> Optional[UserInDB]:
        """Get current user from JWT token."""
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        # TODO: Implement actual database lookup
        # For demo purposes, return a mock user
        return UserInDB(
            id=token_data.user_id or 1,
            email=token_data.email or "demo@example.com",
            full_name="Demo User",
            hashed_password="hashed_password",
            is_active=True,
            searches_used_this_month=5,
            searches_limit=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


# Create global auth service instance
auth_service = AuthService() 
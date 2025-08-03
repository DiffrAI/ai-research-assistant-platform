"""Authentication service and utilities."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import TokenData, UserCreate, UserInDB, UserDB

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id_str: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        role: Optional[str] = payload.get("role")
        
        if user_id_str is None:
            return None
            
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return None
            
        return TokenData(user_id=user_id, email=email, role=role)
    except JWTError:
        return None


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[UserInDB]:
    """Authenticate a user."""
    result = await db.execute(select(UserDB).where(UserDB.email == email))
    user = result.scalar_one_or_none()
    
    if user and verify_password(password, user.hashed_password):
        return UserInDB.model_validate(user, from_attributes=True)
    return None


async def create_user(user_create: UserCreate, db: AsyncSession) -> UserInDB:
    """Create a new user."""
    # Check if user already exists
    result = await db.execute(select(UserDB).where(UserDB.email == user_create.email))
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")
    
    # Create new user
    db_user = UserDB(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
        is_active=True,
        searches_used_this_month=0,
        searches_limit=10,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return UserInDB.model_validate(db_user, from_attributes=True)


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[UserInDB]:
    """Get a user by email."""
    result = await db.execute(select(UserDB).where(UserDB.email == email))
    user = result.scalar_one_or_none()
    return UserInDB.model_validate(user, from_attributes=True) if user else None


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[UserInDB]:
    """Get a user by ID."""
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar_one_or_none()
    return UserInDB.model_validate(user, from_attributes=True) if user else None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserInDB:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = await get_user_by_email(token_data.email, db)
    if user is None:
        raise credentials_exception
    
    return user


async def increment_user_searches(user_id: int, db: AsyncSession) -> bool:
    """Increment user's search count."""
    try:
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.searches_used_this_month += 1
            await db.commit()
            logger.info(f"Incremented searches for user {user_id}")
            return True
    except Exception as e:
        logger.error(f"Error incrementing searches for user {user_id}: {e}")
        await db.rollback()
    return False
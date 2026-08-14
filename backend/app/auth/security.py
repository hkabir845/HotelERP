"""
Authentication and security utilities.

⚠️ CRITICAL: DO NOT MODIFY PASSWORD HASHING WITHOUT TESTING LOGIN!
- Must use bcrypt directly (NOT passlib - causes compatibility issues)
- verify_password() and get_password_hash() are critical for login
- See LOGIN_CRITICAL_COMPONENTS.md for details
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import get_db
from app.models.user import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    ⚠️ CRITICAL: DO NOT CHANGE - Login depends on this!
    Uses bcrypt directly (NOT passlib).
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    ⚠️ CRITICAL: DO NOT CHANGE - Login depends on this!
    Uses bcrypt directly (NOT passlib).
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Bcrypt has a 72-byte limit
    if len(password) > 72:
        password = password[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def authenticate_user(
    db: Session,
    username: str,
    password: str,
    tenant_id: Optional[int] = None
) -> Optional[User]:
    """
    Authenticate a user.
    
    ⚠️ CRITICAL: DO NOT MODIFY WITHOUT TESTING LOGIN!
    - Superusers MUST bypass tenant check (tenant_id can be None)
    - Password verification MUST use verify_password() function
    - User lookup by username OR email must work
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        tenant_id: Optional tenant ID for tenant-specific users
    
    Returns:
        User object if authenticated, None otherwise
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    # Check if user is active
    if not user.is_active:
        return None
    
    # ⚠️ CRITICAL: Superusers MUST bypass tenant check
    # DO NOT enforce tenant_id for superusers - it will break login!
    if not user.is_superuser and tenant_id is not None:
        if user.tenant_id != tenant_id:
            return None
    # If tenant_id is None, allow login (no tenant restriction for superusers)
    
    # Verify password - CRITICAL: Must use verify_password() function
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if username is None or token_type != "access":
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


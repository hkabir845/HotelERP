"""JWT and password utilities (PyJWT + bcrypt)."""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if len(password) > 72:
        password = password[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire, 'type': 'access'})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT token."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def authenticate_user(username: str, password: str, tenant_id: Optional[int] = None):
    """
    Authenticate a user by username/email and password.

    Superusers bypass tenant checks when tenant_id is None.
    """
    user = User.objects.filter(Q(username=username) | Q(email=username)).first()
    if not user or not user.is_active:
        return None

    if not user.is_superuser and tenant_id is not None:
        if user.tenant_id != tenant_id:
            return None

    if not user.check_password(password):
        return None

    return user


def build_token_data(user) -> dict:
    """Build JWT payload fields for a user."""
    return {
        'sub': user.username,
        'user_id': user.id,
        'tenant_id': user.tenant_id,
        'is_superuser': user.is_superuser,
        'role': user.role,
    }

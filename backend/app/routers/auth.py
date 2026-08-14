"""
Authentication router.

⚠️ CRITICAL: DO NOT MODIFY LOGIN ENDPOINT WITHOUT TESTING!
Login must always work. See LOGIN_CRITICAL_COMPONENTS.md for details.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    get_current_user,
    get_current_active_user,
)
from app.middleware.tenant import get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import (
    Token,
    UserLogin,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
)
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token, tags=["Authentication"])
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Supports both regular users and multi-tenant authentication.
    
    ⚠️ CRITICAL: DO NOT MODIFY THIS FUNCTION WITHOUT TESTING LOGIN FIRST!
    - Superadmin must be able to login with tenant_id = None
    - Password verification must use bcrypt (not passlib)
    - CORS must allow localhost:3000
    """
    # Get tenant if subdomain is provided
    tenant_id = None
    tenant = None
    
    if login_data.tenant_subdomain:
        tenant = db.query(Tenant).filter(
            Tenant.subdomain == login_data.tenant_subdomain,
            Tenant.is_active == True
        ).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found or inactive"
            )
        tenant_id = tenant.id
    else:
        # ⚠️ CRITICAL: Superadmin login - MUST allow tenant_id = None
        # DO NOT add tenant requirement here - it will break superadmin login!
        tenant_id = None
    
    # Authenticate user
    user = await authenticate_user(
        db=db,
        username=login_data.username,
        password=login_data.password,
        tenant_id=tenant_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "is_superuser": user.is_superuser,
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# OAuth2 endpoint removed due to compatibility issues with FastAPI/Pydantic versions
# Use /login endpoint instead which supports the same functionality


@router.post("/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "is_superuser": user.is_superuser,
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return current_user


@router.post("/register", response_model=UserResponse, tags=["Authentication"])
async def register(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Note: Only superusers or admins can register new users.
    """
    # Check permissions (only superuser or admin can create users)
    if not current_user.is_superuser and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create users"
        )
    
    # Check if username exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        tenant_id=user_data.tenant_id or current_user.tenant_id,
        is_active=True,
        is_superuser=False,
        is_staff=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


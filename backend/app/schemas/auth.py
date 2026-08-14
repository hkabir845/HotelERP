"""
Authentication schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login request schema."""
    username: str  # Can be username or email
    password: str
    tenant_subdomain: Optional[str] = None  # For multi-tenant login


class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "staff"
    tenant_id: Optional[int] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: str
    tenant_id: Optional[int]
    is_active: bool
    is_superuser: bool
    is_staff: bool
    avatar: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


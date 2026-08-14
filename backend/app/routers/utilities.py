"""
Utilities router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/utilities", tags=["Utilities"])


class SettingsUpdate(BaseModel):
    hotel_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    notification_enabled: Optional[bool] = None


@router.get("/settings")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system settings."""
    # Mock data for now
    settings = {
        "hotel_name": "Hotel ERP",
        "currency": "BDT",
        "timezone": "Asia/Dhaka",
        "date_format": "YYYY-MM-DD",
        "email_enabled": True,
        "sms_enabled": False,
        "notification_enabled": True
    }
    return {"settings": settings}


@router.put("/settings")
async def update_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update system settings."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Superuser only."
        )
    
    # In a real implementation, this would update settings in the database
    return {
        "message": "Settings updated successfully",
        "settings": settings.dict(exclude_unset=True)
    }


@router.get("/users")
async def get_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system users."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Superuser only."
        )
    
    query = db.query(User)
    
    if role and role != 'all':
        # Filter by role if role field exists
        pass
    
    if search:
        query = query.filter(
            User.first_name.ilike(f"%{search}%") |
            User.last_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%")
        )
    
    users = query.all()
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": getattr(user, 'phone', None),
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "role": "admin" if user.is_superuser else "staff",
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    
    return {"users": result}

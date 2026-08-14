"""
Broadcast Message router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/broadcast", tags=["Broadcast"])


@router.get("/messages")
async def get_messages(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get broadcast messages."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data
    messages = [
        {
            "id": 1,
            "message_number": f"MSG-{str(uuid.uuid4())[:8].upper()}",
            "subject": "Welcome Message",
            "content": "Welcome to our hotel! We hope you enjoy your stay.",
            "recipient_type": "all_guests",
            "recipients": ["All Inhouse Guests"],
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
            "created_by": current_user.first_name + " " + current_user.last_name
        },
        {
            "id": 2,
            "message_number": f"MSG-{str(uuid.uuid4())[:8].upper()}",
            "subject": "Staff Meeting Reminder",
            "content": "Reminder: Staff meeting tomorrow at 10 AM in the conference room.",
            "recipient_type": "staff",
            "recipients": ["All Staff Members"],
            "status": "scheduled",
            "sent_at": None,
            "created_by": current_user.first_name + " " + current_user.last_name
        },
        {
            "id": 3,
            "message_number": f"MSG-{str(uuid.uuid4())[:8].upper()}",
            "subject": "Maintenance Notice",
            "content": "Scheduled maintenance in the pool area from 2 PM to 4 PM today.",
            "recipient_type": "all_guests",
            "recipients": ["All Inhouse Guests"],
            "status": "draft",
            "sent_at": None,
            "created_by": current_user.first_name + " " + current_user.last_name
        }
    ]
    
    filtered = messages
    if status and status != 'all':
        filtered = [m for m in filtered if m['status'] == status]
    if search:
        filtered = [m for m in filtered if search.lower() in m['subject'].lower() or
                   search.lower() in m['message_number'].lower()]
    
    return {"messages": filtered}


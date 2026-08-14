"""
Inventory router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/purchases")
async def get_purchases(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inventory purchases."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    purchases = [
        {
            "id": 1,
            "purchase_number": f"PUR-{str(uuid.uuid4())[:8].upper()}",
            "supplier_name": "Supplier ABC",
            "supplier_id": 1,
            "purchase_date": datetime.now().isoformat(),
            "total_amount": 5000.00,
            "items_count": 15,
            "status": "completed",
            "payment_status": "paid"
        },
        {
            "id": 2,
            "purchase_number": f"PUR-{str(uuid.uuid4())[:8].upper()}",
            "supplier_name": "Vendor XYZ",
            "supplier_id": 2,
            "purchase_date": datetime.now().isoformat(),
            "total_amount": 3000.00,
            "items_count": 8,
            "status": "pending",
            "payment_status": "pending"
        }
    ]
    
    filtered = purchases
    if status and status != 'all':
        filtered = [p for p in filtered if p['status'] == status]
    if search:
        filtered = [p for p in filtered if search.lower() in p['purchase_number'].lower() or
                   search.lower() in p['supplier_name'].lower()]
    
    total = len(filtered)
    total_pages = (total + limit - 1) // limit
    paginated = filtered[(page - 1) * limit:page * limit]
    
    return {
        "purchases": paginated,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/requisitions")
async def get_requisitions(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inventory requisitions."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    requisitions = [
        {
            "id": 1,
            "requisition_number": f"REQ-2024-{str(uuid.uuid4())[:8].upper()}",
            "requested_by": current_user.first_name + " " + current_user.last_name,
            "department": "Housekeeping",
            "status": "pending",
            "total_amount": 1250.00,
            "requested_date": datetime.now().isoformat(),
            "approved_date": None,
            "items_count": 5
        },
        {
            "id": 2,
            "requisition_number": f"REQ-2024-{str(uuid.uuid4())[:8].upper()}",
            "requested_by": "John Manager",
            "department": "F&B",
            "status": "approved",
            "total_amount": 3500.00,
            "requested_date": datetime.now().isoformat(),
            "approved_date": datetime.now().isoformat(),
            "items_count": 12
        }
    ]
    
    filtered = requisitions
    if status and status != 'all':
        filtered = [r for r in filtered if r['status'] == status]
    if search:
        filtered = [r for r in filtered if search.lower() in r['requisition_number'].lower() or
                   search.lower() in r['requested_by'].lower()]
    
    return {"requisitions": filtered}


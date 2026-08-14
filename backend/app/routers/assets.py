"""
Assets & Maintenance router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/assets", tags=["Assets & Maintenance"])


@router.get("")
async def get_assets(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assets."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    assets = [
        {
            "id": 1,
            "asset_code": f"AST-{str(uuid.uuid4())[:8].upper()}",
            "name": "Air Conditioning Unit - Room 101",
            "category": "HVAC",
            "type": "Split AC",
            "purchase_date": (datetime.now() - timedelta(days=365)).isoformat(),
            "purchase_cost": 2500.00,
            "current_value": 2000.00,
            "location": "Room 101",
            "status": "active",
            "depreciation_rate": 20.0
        },
        {
            "id": 2,
            "asset_code": f"AST-{str(uuid.uuid4())[:8].upper()}",
            "name": "Commercial Refrigerator",
            "category": "Kitchen Equipment",
            "type": "Refrigerator",
            "purchase_date": (datetime.now() - timedelta(days=730)).isoformat(),
            "purchase_cost": 5000.00,
            "current_value": 3500.00,
            "location": "Kitchen",
            "status": "active",
            "depreciation_rate": 15.0
        },
        {
            "id": 3,
            "asset_code": f"AST-{str(uuid.uuid4())[:8].upper()}",
            "name": "Elevator Motor",
            "category": "Building Systems",
            "type": "Motor",
            "purchase_date": (datetime.now() - timedelta(days=180)).isoformat(),
            "purchase_cost": 8000.00,
            "current_value": 7500.00,
            "location": "Elevator Shaft",
            "status": "maintenance",
            "depreciation_rate": 10.0
        }
    ]
    
    filtered = assets
    if status and status != 'all':
        filtered = [a for a in filtered if a['status'] == status]
    if search:
        filtered = [a for a in filtered if search.lower() in a['asset_code'].lower() or
                   search.lower() in a['name'].lower() or
                   search.lower() in a['location'].lower()]
    
    return {"assets": filtered}


@router.get("/maintenance-requests")
async def get_maintenance_requests(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get maintenance requests."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data
    requests = [
        {
            "id": 1,
            "request_number": f"MR-{str(uuid.uuid4())[:8].upper()}",
            "asset_name": "Air Conditioning Unit - Room 101",
            "asset_code": "AST-ABC123",
            "location": "Room 101",
            "requested_by": current_user.first_name + " " + current_user.last_name,
            "priority": "urgent",
            "status": "pending",
            "issue_description": "AC not cooling properly",
            "requested_date": datetime.now().isoformat(),
            "assigned_to": None,
            "completed_date": None
        },
        {
            "id": 2,
            "request_number": f"MR-{str(uuid.uuid4())[:8].upper()}",
            "asset_name": "Commercial Refrigerator",
            "asset_code": "AST-DEF456",
            "location": "Kitchen",
            "requested_by": "Kitchen Staff",
            "priority": "high",
            "status": "in_progress",
            "issue_description": "Temperature fluctuation",
            "requested_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "assigned_to": "Maintenance Team",
            "completed_date": None
        },
        {
            "id": 3,
            "request_number": f"MR-{str(uuid.uuid4())[:8].upper()}",
            "asset_name": "Elevator Motor",
            "asset_code": "AST-GHI789",
            "location": "Elevator Shaft",
            "requested_by": "Building Manager",
            "priority": "urgent",
            "status": "completed",
            "issue_description": "Routine maintenance",
            "requested_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "assigned_to": "Maintenance Team",
            "completed_date": datetime.now().isoformat()
        }
    ]
    
    filtered = requests
    if status and status != 'all':
        filtered = [r for r in filtered if r['status'] == status]
    if priority and priority != 'all':
        filtered = [r for r in filtered if r['priority'] == priority]
    if search:
        filtered = [r for r in filtered if search.lower() in r['request_number'].lower() or
                   search.lower() in r['asset_name'].lower() or
                   search.lower() in r['location'].lower()]
    
    return {"requests": filtered}


@router.get("/work-orders")
async def get_work_orders(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get work orders."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data
    work_orders = [
        {
            "id": 1,
            "work_order_number": f"WO-{str(uuid.uuid4())[:8].upper()}",
            "maintenance_request_id": 1,
            "asset_name": "Air Conditioning Unit - Room 101",
            "location": "Room 101",
            "assigned_to": "Maintenance Team",
            "priority": "urgent",
            "status": "in_progress",
            "estimated_cost": 500.00,
            "actual_cost": None,
            "scheduled_date": datetime.now().isoformat(),
            "started_date": datetime.now().isoformat(),
            "completed_date": None,
            "description": "AC repair and maintenance"
        },
        {
            "id": 2,
            "work_order_number": f"WO-{str(uuid.uuid4())[:8].upper()}",
            "maintenance_request_id": 2,
            "asset_name": "Commercial Refrigerator",
            "location": "Kitchen",
            "assigned_to": "Maintenance Team",
            "priority": "high",
            "status": "approved",
            "estimated_cost": 800.00,
            "actual_cost": None,
            "scheduled_date": (datetime.now().replace(day=datetime.now().day + 2)).isoformat(),
            "started_date": None,
            "completed_date": None,
            "description": "Temperature control system repair"
        },
        {
            "id": 3,
            "work_order_number": f"WO-{str(uuid.uuid4())[:8].upper()}",
            "maintenance_request_id": 3,
            "asset_name": "Elevator Motor",
            "location": "Elevator Shaft",
            "assigned_to": "Maintenance Team",
            "priority": "medium",
            "status": "completed",
            "estimated_cost": 1200.00,
            "actual_cost": 1150.00,
            "scheduled_date": (datetime.now().replace(day=datetime.now().day - 5)).isoformat(),
            "started_date": (datetime.now().replace(day=datetime.now().day - 5)).isoformat(),
            "completed_date": datetime.now().isoformat(),
            "description": "Routine maintenance completed"
        }
    ]
    
    filtered = work_orders
    if status and status != 'all':
        filtered = [wo for wo in filtered if wo['status'] == status]
    if priority and priority != 'all':
        filtered = [wo for wo in filtered if wo['priority'] == priority]
    if search:
        filtered = [wo for wo in filtered if search.lower() in wo['work_order_number'].lower() or
                   search.lower() in wo['asset_name'].lower() or
                   search.lower() in wo['location'].lower()]
    
    return {"work_orders": filtered}

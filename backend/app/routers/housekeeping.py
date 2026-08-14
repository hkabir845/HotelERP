"""
Housekeeping router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Room, RoomType
from app.models.room import RoomStatusEnum
from app.models.housekeeping import HousekeepingTask, RoomStatus, TaskStatus, TaskType, TaskPriority
from app.routers.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])


@router.get("/wake-up-calls")
async def get_wake_up_calls(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wake-up calls."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    calls = [
        {
            "id": 1,
            "room_number": "101",
            "guest_name": "John Doe",
            "wake_up_time": (datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)).isoformat(),
            "status": "scheduled",
            "completed_at": None,
            "notes": "Early morning flight"
        },
        {
            "id": 2,
            "room_number": "205",
            "guest_name": "Jane Smith",
            "wake_up_time": (datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)).isoformat(),
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "notes": None
        }
    ]
    
    filtered = calls
    if status and status != 'all':
        filtered = [c for c in filtered if c['status'] == status]
    if search:
        filtered = [c for c in filtered if search.lower() in c['room_number'].lower() or
                   search.lower() in c['guest_name'].lower()]
    
    return {"calls": filtered}


@router.get("/lost-found")
async def get_lost_found(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lost & found items."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock data for now
    items = [
        {
            "id": 1,
            "item_number": f"LF-{str(uuid.uuid4())[:8].upper()}",
            "item_name": "Mobile Phone",
            "description": "Black iPhone 13",
            "location_found": "Lobby",
            "room_number": None,
            "guest_name": None,
            "status": "found",
            "found_date": datetime.now().isoformat(),
            "claimed_date": None,
            "category": "Electronics"
        },
        {
            "id": 2,
            "item_number": f"LF-{str(uuid.uuid4())[:8].upper()}",
            "item_name": "Wallet",
            "description": "Brown leather wallet with credit cards",
            "location_found": "Restaurant",
            "room_number": "101",
            "guest_name": "John Doe",
            "status": "claimed",
            "found_date": (datetime.now().replace(day=datetime.now().day - 2)).isoformat(),
            "claimed_date": datetime.now().isoformat(),
            "category": "Personal Items"
        }
    ]
    
    filtered = items
    if status and status != 'all':
        filtered = [i for i in filtered if i['status'] == status]
    if search:
        filtered = [i for i in filtered if search.lower() in i['item_name'].lower() or
                   search.lower() in (i.get('room_number') or '').lower() or
                   search.lower() in (i.get('guest_name') or '').lower()]
    
    return {"items": filtered}


@router.get("/tasks")
async def get_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get housekeeping tasks."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    query = db.query(HousekeepingTask).join(Room)
    
    if tenant_id:
        query = query.filter(HousekeepingTask.tenant_id == tenant_id)
    
    if status:
        try:
            status_enum = TaskStatus(status)
            query = query.filter(HousekeepingTask.status == status_enum)
        except ValueError:
            pass
    
    if priority:
        try:
            priority_enum = TaskPriority(priority)
            query = query.filter(HousekeepingTask.priority == priority_enum)
        except ValueError:
            pass
    
    if search:
        query = query.filter(
            or_(
                Room.room_number.ilike(f"%{search}%"),
                HousekeepingTask.description.ilike(f"%{search}%")
            )
        )
    
    tasks = query.order_by(HousekeepingTask.scheduled_date.desc()).all()
    
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "task_number": f"TASK-{task.id}",
            "room": {
                "id": task.room.id,
                "room_number": task.room.room_number,
                "room_type": task.room.room_type.name
            },
            "task_type": task.task_type.value,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": {
                "id": task.assigned_to.id,
                "name": f"{task.assigned_to.first_name} {task.assigned_to.last_name}"
            } if task.assigned_to else None,
            "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "description": task.description
        })
    
    return {"tasks": result}


@router.get("/rooms/status")
async def get_room_status(
    status_filter: Optional[str] = Query(None, alias="status"),
    floor: Optional[int] = Query(None),
    room_type_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all rooms with their status for housekeeping.
    """
    # Build query
    query = db.query(Room).join(RoomType)
    
    # Apply tenant filter
    if current_user.tenant_id:
        query = query.filter(Room.tenant_id == current_user.tenant_id)
    elif not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Apply filters
    if status_filter:
        try:
            status_enum = RoomStatusEnum(status_filter)
            query = query.filter(Room.status == status_enum)
        except ValueError:
            pass
    
    if floor is not None:
        query = query.filter(Room.floor == floor)
    
    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    
    if search:
        query = query.filter(
            or_(
                Room.room_number.ilike(f"%{search}%"),
                RoomType.name.ilike(f"%{search}%")
            )
        )
    
    rooms = query.order_by(Room.floor, Room.room_number).all()
    
    # Get housekeeping tasks for rooms
    room_ids = [room.id for room in rooms]
    tasks = db.query(HousekeepingTask).filter(
        and_(
            HousekeepingTask.room_id.in_(room_ids),
            HousekeepingTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        )
    ).all()
    
    tasks_by_room = {task.room_id: task for task in tasks}
    
    # Get room status records
    room_statuses = db.query(RoomStatus).filter(
        RoomStatus.room_id.in_(room_ids)
    ).all()
    
    status_by_room = {rs.room_id: rs for rs in room_statuses}
    
    # Format response
    result = []
    for room in rooms:
        room_status = status_by_room.get(room.id)
        task = tasks_by_room.get(room.id)
        
        result.append({
            "id": room.id,
            "room_number": room.room_number,
            "floor": room.floor,
            "room_type": {
                "id": room.room_type.id,
                "name": room.room_type.name,
                "max_occupancy": room.room_type.max_occupancy
            },
            "status": room.status.value,
            "bed_type": room.bed_type,
            "view": room.view,
            "housekeeping_status": room_status.housekeeping_status if room_status else None,
            "last_cleaned": room_status.last_cleaned.isoformat() if room_status and room_status.last_cleaned else None,
            "last_inspected": room_status.last_inspected.isoformat() if room_status and room_status.last_inspected else None,
            "next_cleaning_due": room_status.next_cleaning_due.isoformat() if room_status and room_status.next_cleaning_due else None,
            "has_pending_task": task is not None,
            "task_type": task.task_type.value if task else None,
            "task_status": task.status.value if task else None,
            "notes": room_status.notes if room_status else room.notes,
            "is_active": room.is_active
        })
    
    return {
        "rooms": result,
        "total": len(result),
        "summary": {
            "available": len([r for r in result if r["status"] == "available"]),
            "occupied": len([r for r in result if r["status"] == "occupied"]),
            "cleaning": len([r for r in result if r["status"] == "cleaning"]),
            "maintenance": len([r for r in result if r["status"] == "maintenance"]),
            "out_of_order": len([r for r in result if r["status"] == "out_of_order"]),
            "reserved": len([r for r in result if r["status"] == "reserved"]),
        }
    }


@router.get("/rooms/floors")
async def get_floors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of floors."""
    query = db.query(Room.floor).distinct()
    
    if current_user.tenant_id:
        query = query.filter(Room.tenant_id == current_user.tenant_id)
    elif not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    floors = [f[0] for f in query.order_by(Room.floor).all() if f[0] is not None]
    return {"floors": floors}


@router.get("/rooms/types")
async def get_room_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of room types."""
    query = db.query(RoomType)
    
    if current_user.tenant_id:
        query = query.filter(RoomType.tenant_id == current_user.tenant_id)
    elif not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    room_types = query.filter(RoomType.is_active == True).all()
    return {
        "room_types": [
            {
                "id": rt.id,
                "name": rt.name,
                "description": rt.description,
                "max_occupancy": rt.max_occupancy
            }
            for rt in room_types
        ]
    }


@router.patch("/rooms/{room_id}/status")
async def update_room_status(
    room_id: int,
    status: str = Query(...),
    housekeeping_status: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update room status."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check tenant access
    if current_user.tenant_id and room.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update room status
    try:
        room.status = RoomStatusEnum(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    # Update or create room status record
    room_status = db.query(RoomStatus).filter(RoomStatus.room_id == room_id).first()
    if not room_status:
        room_status = RoomStatus(
            tenant_id=room.tenant_id,
            room_id=room_id,
            status=status,
            housekeeping_status=housekeeping_status or "dirty"
        )
        db.add(room_status)
    else:
        room_status.status = status
        if housekeeping_status:
            room_status.housekeeping_status = housekeeping_status
        if notes:
            room_status.notes = notes
        room_status.updated_by_id = current_user.id
    
    db.commit()
    
    return {
        "message": "Room status updated successfully",
        "room_id": room_id,
        "status": status
    }

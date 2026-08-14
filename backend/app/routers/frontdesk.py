"""
Frontdesk router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models import Room, RoomType, Reservation, Guest
from app.models.room import RoomStatusEnum
from app.models.reservation import ReservationStatus
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/frontdesk", tags=["Frontdesk"])


@router.get("/room-rack")
async def get_room_rack(
    floor: Optional[int] = Query(None),
    room_type_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    date_filter: Optional[str] = Query(None),  # YYYY-MM-DD format
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get room rack data - all rooms with their current reservations and status.
    This is the main endpoint for the front desk room rack display.
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
    if floor is not None:
        query = query.filter(Room.floor == floor)
    
    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    
    if status_filter:
        try:
            status_enum = RoomStatusEnum(status_filter)
            query = query.filter(Room.status == status_enum)
        except ValueError:
            pass
    
    if search:
        query = query.filter(
            or_(
                Room.room_number.ilike(f"%{search}%"),
                RoomType.name.ilike(f"%{search}%")
            )
        )
    
    rooms = query.order_by(Room.floor, Room.room_number).all()
    
    # Get active reservations for these rooms
    room_ids = [room.id for room in rooms]
    
    # Filter date for reservations
    filter_date = datetime.now().date()
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    # Get reservations that are active on the filter date
    # A reservation is active if check_in_date <= filter_date < check_out_date
    filter_datetime_start = datetime.combine(filter_date, datetime.min.time())
    filter_datetime_end = datetime.combine(filter_date, datetime.max.time())
    
    reservations = db.query(Reservation).join(Guest).filter(
        and_(
            Reservation.room_id.in_(room_ids),
            Reservation.status.in_([
                ReservationStatus.CONFIRMED,
                ReservationStatus.CHECKED_IN,
                ReservationStatus.PENDING
            ]),
            Reservation.check_in_date <= filter_datetime_end,
            Reservation.check_out_date > filter_datetime_start
        )
    ).all()
    
    # Group reservations by room_id
    reservations_by_room = {}
    for reservation in reservations:
        if reservation.room_id:
            if reservation.room_id not in reservations_by_room:
                reservations_by_room[reservation.room_id] = []
            reservations_by_room[reservation.room_id].append(reservation)
    
    # Format response
    result = []
    for room in rooms:
        room_reservations = reservations_by_room.get(room.id, [])
        
        # Get current/active reservation
        current_reservation = None
        for res in room_reservations:
            if res.status == ReservationStatus.CHECKED_IN:
                current_reservation = res
                break
            elif res.status == ReservationStatus.CONFIRMED and not current_reservation:
                # Use confirmed reservation if no checked-in
                current_reservation = res
        
        # If no checked-in, use the first confirmed reservation
        if not current_reservation and room_reservations:
            current_reservation = room_reservations[0]
        
        result.append({
            "id": room.id,
            "room_number": room.room_number,
            "floor": room.floor,
            "room_type": {
                "id": room.room_type.id,
                "name": room.room_type.name,
                "max_occupancy": room.room_type.max_occupancy,
                "base_rate": float(room.room_type.base_rate) if room.room_type.base_rate else None
            },
            "status": room.status.value,
            "bed_type": room.bed_type,
            "view": room.view,
            "rack_rate": float(room.rack_rate) if room.rack_rate else None,
            "is_active": room.is_active,
            "current_reservation": {
                "id": current_reservation.id,
                "reservation_number": current_reservation.reservation_number,
                "guest": {
                    "id": current_reservation.guest.id,
                    "name": f"{current_reservation.guest.first_name} {current_reservation.guest.last_name}",
                    "first_name": current_reservation.guest.first_name,
                    "last_name": current_reservation.guest.last_name,
                    "phone": current_reservation.guest.phone,
                    "email": current_reservation.guest.email,
                    "is_vip": current_reservation.guest.is_vip
                },
                "check_in_date": current_reservation.check_in_date.isoformat() if current_reservation.check_in_date else None,
                "check_out_date": current_reservation.check_out_date.isoformat() if current_reservation.check_out_date else None,
                "actual_check_in": current_reservation.actual_check_in.isoformat() if current_reservation.actual_check_in else None,
                "actual_check_out": current_reservation.actual_check_out.isoformat() if current_reservation.actual_check_out else None,
                "status": current_reservation.status.value,
                "reservation_type": current_reservation.reservation_type.value,
                "adults": current_reservation.adults,
                "children": current_reservation.children,
                "room_rate": float(current_reservation.room_rate) if current_reservation.room_rate else None,
                "total_amount": float(current_reservation.total_amount) if current_reservation.total_amount else None,
                "paid_amount": float(current_reservation.paid_amount) if current_reservation.paid_amount else None,
                "balance": float(current_reservation.balance) if current_reservation.balance else None,
                "source": current_reservation.source,
                "nights": (current_reservation.check_out_date - current_reservation.check_in_date).days if current_reservation.check_in_date and current_reservation.check_out_date else 0
            } if current_reservation else None,
            "all_reservations": [
                {
                    "id": res.id,
                    "reservation_number": res.reservation_number,
                    "guest_name": f"{res.guest.first_name} {res.guest.last_name}",
                    "check_in_date": res.check_in_date.isoformat() if res.check_in_date else None,
                    "check_out_date": res.check_out_date.isoformat() if res.check_out_date else None,
                    "status": res.status.value,
                    "nights": (res.check_out_date - res.check_in_date).days if res.check_in_date and res.check_out_date else 0
                }
                for res in room_reservations
            ]
        })
    
    # Calculate summary statistics
    total_rooms = len(result)
    available_rooms = len([r for r in result if r["status"] == "available" and not r["current_reservation"]])
    occupied_rooms = len([r for r in result if r["status"] == "occupied" or r["current_reservation"]])
    reserved_rooms = len([r for r in result if r["status"] == "reserved"])
    out_of_order = len([r for r in result if r["status"] == "out_of_order"])
    maintenance = len([r for r in result if r["status"] == "maintenance"])
    cleaning = len([r for r in result if r["status"] == "cleaning"])
    
    return {
        "rooms": result,
        "total": total_rooms,
        "summary": {
            "available": available_rooms,
            "occupied": occupied_rooms,
            "reserved": reserved_rooms,
            "out_of_order": out_of_order,
            "maintenance": maintenance,
            "cleaning": cleaning
        },
        "filter_date": filter_date.isoformat()
    }


@router.get("/room-rack/floors")
async def get_floors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of floors for filtering."""
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


@router.get("/room-rack/types")
async def get_room_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of room types for filtering."""
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


"""
Reservations router.
⚠️ CRITICAL: DO NOT MODIFY LOGIN ENDPOINT - This is separate from auth!
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.database import get_db
from app.models import Room, RoomType, Reservation, Guest
from app.models.room import RoomStatusEnum
from app.models.reservation import ReservationStatus, ReservationType
from app.routers.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter(prefix="/reservations", tags=["Reservations"])


class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    is_vip: bool = False


class ReservationCreate(BaseModel):
    # Guest (create new or use existing)
    guest_id: Optional[int] = None
    guest: Optional[GuestCreate] = None
    
    # Room
    room_id: Optional[int] = None
    room_type_id: Optional[int] = None
    
    # Dates
    check_in_date: str  # ISO format
    check_out_date: str  # ISO format
    
    # Reservation details
    reservation_type: str = "individual"  # individual, group, corporate, walk_in
    status: str = "pending"  # pending, confirmed
    
    # Guests
    adults: int = 1
    children: int = 0
    
    # Pricing
    room_rate: Decimal
    total_amount: Optional[Decimal] = None
    
    # Payment
    paid_amount: Decimal = Decimal(0)
    
    # Additional info
    source: Optional[str] = None
    booking_agent: Optional[str] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
async def get_reservations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of reservations with pagination."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    query = db.query(Reservation).join(Guest)
    
    if tenant_id:
        query = query.filter(Reservation.tenant_id == tenant_id)
    
    if status:
        try:
            status_enum = ReservationStatus(status)
            query = query.filter(Reservation.status == status_enum)
        except ValueError:
            pass
    
    if search:
        query = query.filter(
            or_(
                Reservation.reservation_number.ilike(f"%{search}%"),
                Guest.first_name.ilike(f"%{search}%"),
                Guest.last_name.ilike(f"%{search}%"),
                Guest.email.ilike(f"%{search}%"),
                Guest.phone.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    
    reservations = query.order_by(Reservation.check_in_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for res in reservations:
        nights = 0
        if res.check_in_date and res.check_out_date:
            nights = (res.check_out_date - res.check_in_date).days
        
        result.append({
            "id": res.id,
            "reservation_number": res.reservation_number,
            "guest": {
                "id": res.guest.id,
                "name": f"{res.guest.first_name} {res.guest.last_name}",
                "email": res.guest.email,
                "phone": res.guest.phone,
                "is_vip": res.guest.is_vip
            },
            "room": {
                "id": res.room.id,
                "room_number": res.room.room_number,
                "room_type": res.room.room_type.name
            } if res.room else None,
            "check_in_date": res.check_in_date.isoformat() if res.check_in_date else None,
            "check_out_date": res.check_out_date.isoformat() if res.check_out_date else None,
            "status": res.status.value,
            "reservation_type": res.reservation_type.value,
            "adults": res.adults,
            "children": res.children,
            "room_rate": float(res.room_rate) if res.room_rate else None,
            "total_amount": float(res.total_amount) if res.total_amount else None,
            "paid_amount": float(res.paid_amount) if res.paid_amount else None,
            "balance": float(res.balance) if res.balance else None,
            "source": res.source,
            "nights": nights
        })
    
    return {
        "reservations": result,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.post("/create")
async def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new reservation.
    Can create a new guest or use an existing one.
    """
    # Get tenant_id
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access required"
        )
    
    # Handle guest (create new or use existing)
    guest_id = reservation_data.guest_id
    if not guest_id:
        if not reservation_data.guest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either guest_id or guest information is required"
            )
        
        # Create new guest
        guest_data = reservation_data.guest
        
        # Check if guest already exists by email or phone
        existing_guest = None
        if guest_data.email:
            existing_guest = db.query(Guest).filter(
                and_(
                    Guest.email == guest_data.email,
                    Guest.tenant_id == tenant_id
                )
            ).first()
        elif guest_data.phone:
            existing_guest = db.query(Guest).filter(
                and_(
                    Guest.phone == guest_data.phone,
                    Guest.tenant_id == tenant_id
                )
            ).first()
        
        if existing_guest:
            guest_id = existing_guest.id
        else:
            # Parse date of birth
            dob = None
            if guest_data.date_of_birth:
                try:
                    dob = datetime.strptime(guest_data.date_of_birth, "%Y-%m-%d").date()
                except ValueError:
                    pass
            
            new_guest = Guest(
                tenant_id=tenant_id,
                first_name=guest_data.first_name,
                last_name=guest_data.last_name,
                email=guest_data.email,
                phone=guest_data.phone,
                mobile=guest_data.mobile,
                address_line1=guest_data.address_line1,
                city=guest_data.city,
                state=guest_data.state,
                country=guest_data.country,
                postal_code=guest_data.postal_code,
                id_type=guest_data.id_type,
                id_number=guest_data.id_number,
                date_of_birth=dob,
                nationality=guest_data.nationality,
                gender=guest_data.gender,
                is_vip=guest_data.is_vip
            )
            db.add(new_guest)
            db.flush()
            guest_id = new_guest.id
    
    # Verify guest exists
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found"
        )
    
    # Handle room
    room_id = reservation_data.room_id
    if not room_id and reservation_data.room_type_id:
        # Find available room of this type
        available_room = db.query(Room).filter(
            and_(
                Room.room_type_id == reservation_data.room_type_id,
                Room.tenant_id == tenant_id,
                Room.status == RoomStatusEnum.AVAILABLE,
                Room.is_active == True
            )
        ).first()
        
        if available_room:
            room_id = available_room.id
    
    # Parse dates
    try:
        check_in = datetime.fromisoformat(reservation_data.check_in_date.replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(reservation_data.check_out_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Validate dates
    if check_out <= check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )
    
    # Calculate nights
    nights = (check_out - check_in).days
    
    # Calculate total amount if not provided
    total_amount = reservation_data.total_amount
    if not total_amount:
        total_amount = reservation_data.room_rate * Decimal(nights)
    
    balance = total_amount - reservation_data.paid_amount
    
    # Generate reservation number
    reservation_number = f"RES-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create reservation
    reservation = Reservation(
        tenant_id=tenant_id,
        reservation_number=reservation_number,
        guest_id=guest_id,
        room_id=room_id,
        check_in_date=check_in,
        check_out_date=check_out,
        status=ReservationStatus(reservation_data.status),
        reservation_type=ReservationType(reservation_data.reservation_type),
        room_rate=reservation_data.room_rate,
        total_amount=total_amount,
        paid_amount=reservation_data.paid_amount,
        balance=balance,
        adults=reservation_data.adults,
        children=reservation_data.children,
        source=reservation_data.source,
        booking_agent=reservation_data.booking_agent,
        special_requests=reservation_data.special_requests,
        notes=reservation_data.notes,
        created_by_id=current_user.id
    )
    
    db.add(reservation)
    
    # Update room status if room is assigned
    if room_id:
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.status = RoomStatusEnum.RESERVED
    
    db.commit()
    db.refresh(reservation)
    
    return {
        "message": "Reservation created successfully",
        "reservation": {
            "id": reservation.id,
            "reservation_number": reservation.reservation_number,
            "guest_name": f"{guest.first_name} {guest.last_name}",
            "check_in_date": reservation.check_in_date.isoformat(),
            "check_out_date": reservation.check_out_date.isoformat(),
            "nights": nights,
            "total_amount": float(total_amount),
            "balance": float(balance)
        }
    }


@router.get("/guests/search")
async def search_guests(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Search for existing guests."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    search_query = f"%{query}%"
    guests = db.query(Guest).filter(
        and_(
            Guest.tenant_id == tenant_id,
            or_(
                Guest.first_name.ilike(search_query),
                Guest.last_name.ilike(search_query),
                Guest.email.ilike(search_query),
                Guest.phone.ilike(search_query),
                Guest.id_number.ilike(search_query)
            )
        )
    ).limit(limit).all()
    
    return {
        "guests": [
            {
                "id": g.id,
                "name": f"{g.first_name} {g.last_name}",
                "email": g.email,
                "phone": g.phone,
                "is_vip": g.is_vip,
                "loyalty_points": g.loyalty_points
            }
            for g in guests
        ]
    }


@router.get("/rooms/available")
async def get_available_rooms(
    check_in: str,
    check_out: str,
    room_type_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available rooms for given dates."""
    tenant_id = current_user.tenant_id
    if not tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        check_in_date = datetime.fromisoformat(check_in.replace('Z', '+00:00'))
        check_out_date = datetime.fromisoformat(check_out.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format"
        )
    
    # Get all rooms
    query = db.query(Room).join(RoomType).filter(
        and_(
            Room.tenant_id == tenant_id,
            Room.is_active == True,
            Room.status.in_([RoomStatusEnum.AVAILABLE, RoomStatusEnum.RESERVED])
        )
    )
    
    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    
    all_rooms = query.all()
    
    # Get conflicting reservations
    conflicting_reservations = db.query(Reservation).filter(
        and_(
            Reservation.tenant_id == tenant_id,
            Reservation.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.PENDING]),
            Reservation.room_id.isnot(None),
            or_(
                and_(
                    Reservation.check_in_date < check_out_date,
                    Reservation.check_out_date > check_in_date
                )
            )
        )
    ).all()
    
    conflicting_room_ids = {r.room_id for r in conflicting_reservations if r.room_id}
    
    # Filter available rooms
    available_rooms = [
        room for room in all_rooms
        if room.id not in conflicting_room_ids or room.status == RoomStatusEnum.AVAILABLE
    ]
    
    return {
        "rooms": [
            {
                "id": room.id,
                "room_number": room.room_number,
                "floor": room.floor,
                "room_type": {
                    "id": room.room_type.id,
                    "name": room.room_type.name,
                    "base_rate": float(room.room_type.base_rate) if room.room_type.base_rate else None
                },
                "rack_rate": float(room.rack_rate) if room.rack_rate else None,
                "bed_type": room.bed_type,
                "view": room.view
            }
            for room in available_rooms
        ],
        "total": len(available_rooms)
    }

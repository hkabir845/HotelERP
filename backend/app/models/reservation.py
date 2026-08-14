"""
Reservation model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ReservationStatus(str, enum.Enum):
    """Reservation status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ReservationType(str, enum.Enum):
    """Reservation type."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    CORPORATE = "corporate"
    WALK_IN = "walk_in"


class Reservation(Base):
    """Reservation model."""
    
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    reservation_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Guest
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    guest = relationship("Guest", back_populates="reservations")
    
    # Room
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    room = relationship("Room", back_populates="reservations")
    
    # Dates
    check_in_date = Column(DateTime(timezone=True), nullable=False, index=True)
    check_out_date = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_check_in = Column(DateTime(timezone=True), nullable=True)
    actual_check_out = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)
    reservation_type = Column(Enum(ReservationType), default=ReservationType.INDIVIDUAL)
    
    # Pricing
    room_rate = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    balance = Column(Numeric(10, 2), nullable=False)
    
    # Guests
    adults = Column(Integer, default=1)
    children = Column(Integer, default=0)
    
    # Special requests
    special_requests = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Source
    source = Column(String(100), nullable=True)  # Online, Phone, Walk-in, etc.
    booking_agent = Column(String(100), nullable=True)
    
    # Created by
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="reservations")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, reservation_number='{self.reservation_number}', status='{self.status}')>"


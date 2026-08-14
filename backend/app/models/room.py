"""
Room and RoomType models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RoomStatusEnum(str, enum.Enum):
    """Room status."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OUT_OF_ORDER = "out_of_order"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"
    RESERVED = "reserved"


class RoomType(Base):
    """Room type model."""
    
    __tablename__ = "room_types"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_occupancy = Column(Integer, default=2)
    base_rate = Column(Numeric(10, 2), nullable=False)
    amenities = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tenant = relationship("Tenant")
    rooms = relationship("Room", back_populates="room_type")
    
    def __repr__(self):
        return f"<RoomType(id={self.id}, name='{self.name}')>"


class Room(Base):
    """Room model."""
    
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    room_number = Column(String(20), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    floor = Column(Integer, nullable=True)
    status = Column(Enum(RoomStatusEnum), default=RoomStatusEnum.AVAILABLE)
    
    # Room details
    bed_type = Column(String(50), nullable=True)
    view = Column(String(100), nullable=True)
    smoking_allowed = Column(Boolean, default=False)
    
    # Pricing
    rack_rate = Column(Numeric(10, 2), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="rooms")
    room_type = relationship("RoomType", back_populates="rooms")
    reservations = relationship("Reservation", back_populates="room")
    housekeeping_tasks = relationship("HousekeepingTask", back_populates="room")
    
    def __repr__(self):
        return f"<Room(id={self.id}, room_number='{self.room_number}', status='{self.status}')>"


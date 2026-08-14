"""
Housekeeping models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, enum.Enum):
    """Task type."""
    CLEANING = "cleaning"
    INSPECTION = "inspection"
    MAINTENANCE = "maintenance"
    DEEP_CLEAN = "deep_clean"
    TURNDOWN = "turndown"


class RoomStatus(Base):
    """Room status tracking."""
    
    __tablename__ = "room_status"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    room = relationship("Room")
    
    status = Column(String(50), nullable=False)  # Available, Occupied, OOO, etc.
    housekeeping_status = Column(String(50), nullable=True)  # Clean, Dirty, Inspected, etc.
    
    last_cleaned = Column(DateTime(timezone=True), nullable=True)
    last_inspected = Column(DateTime(timezone=True), nullable=True)
    next_cleaning_due = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = relationship("User")
    
    def __repr__(self):
        return f"<RoomStatus(id={self.id}, room_id={self.room_id}, status='{self.status}')>"


class HousekeepingTask(Base):
    """Housekeeping task model."""
    
    __tablename__ = "housekeeping_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    room = relationship("Room", back_populates="housekeeping_tasks")
    
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Details
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    inspection_notes = Column(Text, nullable=True)
    
    # Quality check
    inspected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspected_by = relationship("User", foreign_keys=[inspected_by_id])
    inspection_date = Column(DateTime(timezone=True), nullable=True)
    passed_inspection = Column(Boolean, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HousekeepingTask(id={self.id}, room_id={self.room_id}, status='{self.status}')>"


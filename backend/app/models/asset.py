"""
Asset & Maintenance models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AssetStatus(str, enum.Enum):
    """Asset status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISPOSED = "disposed"
    UNDER_MAINTENANCE = "under_maintenance"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenanceType(str, enum.Enum):
    """Maintenance type."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"


class AssetCategory(Base):
    """Asset category model."""
    
    __tablename__ = "asset_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    depreciation_rate = Column(Numeric(5, 2), nullable=True)  # Annual depreciation percentage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assets = relationship("Asset", back_populates="category")
    
    def __repr__(self):
        return f"<AssetCategory(id={self.id}, name='{self.name}')>"


class Asset(Base):
    """Asset model."""
    
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    asset_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)
    category = relationship("AssetCategory", back_populates="assets")
    
    # Location
    location = Column(String(200), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    
    # Purchase details
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Numeric(15, 2), nullable=True)
    supplier = Column(String(200), nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    
    # Current value
    current_value = Column(Numeric(15, 2), nullable=True)
    depreciation_method = Column(String(50), nullable=True)  # Straight-line, Declining balance, etc.
    depreciation_rate = Column(Numeric(5, 2), nullable=True)
    accumulated_depreciation = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    condition = Column(String(50), nullable=True)  # Excellent, Good, Fair, Poor
    
    # Maintenance
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_due = Column(Date, nullable=True)
    
    # Metadata
    serial_number = Column(String(100), nullable=True)
    model_number = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    maintenance_requests = relationship("MaintenanceRequest", back_populates="asset")
    maintenance_schedules = relationship("MaintenanceSchedule", back_populates="asset")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, asset_code='{self.asset_code}', name='{self.name}')>"


class MaintenanceRequest(Base):
    """Maintenance request model."""
    
    __tablename__ = "maintenance_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    asset = relationship("Asset", back_populates="maintenance_requests")
    
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Description
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reported_issue = Column(Text, nullable=True)
    
    # Assignment
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    # Dates
    requested_date = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cost
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    
    # Resolution
    work_performed = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    parts_used = Column(Text, nullable=True)
    
    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MaintenanceRequest(id={self.id}, request_number='{self.request_number}', status='{self.status}')>"


class MaintenanceSchedule(Base):
    """Preventive maintenance schedule model."""
    
    __tablename__ = "maintenance_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    asset = relationship("Asset", back_populates="maintenance_schedules")
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule
    frequency_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    frequency_value = Column(Integer, default=1)  # Every X days/weeks/months
    next_due_date = Column(Date, nullable=False, index=True)
    last_performed = Column(Date, nullable=True)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<MaintenanceSchedule(id={self.id}, asset_id={self.asset_id}, next_due='{self.next_due_date}')>"


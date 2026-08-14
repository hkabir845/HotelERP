"""
Work Order models - Can be converted to bills after approval.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class WorkOrderStatus(str, enum.Enum):
    """Work order status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CONVERTED_TO_BILL = "converted_to_bill"


class WorkOrderPriority(str, enum.Enum):
    """Work order priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkOrder(Base):
    """Work Order model - Can be converted to bill after approval."""
    
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    work_order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic Info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    work_type = Column(String(100), nullable=True)  # Maintenance, Repair, Installation, etc.
    
    # Location
    location = Column(String(200), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    
    # Status & Priority
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.DRAFT)
    priority = Column(Enum(WorkOrderPriority), default=WorkOrderPriority.MEDIUM)
    
    # Assignment
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    # Dates
    requested_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Costing
    estimated_cost = Column(Numeric(15, 2), default=0)
    actual_cost = Column(Numeric(15, 2), default=0)
    labor_cost = Column(Numeric(15, 2), default=0)
    material_cost = Column(Numeric(15, 2), default=0)
    other_cost = Column(Numeric(15, 2), default=0)
    
    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Bill Conversion
    converted_to_bill = Column(Boolean, default=False)
    bill_id = Column(Integer, nullable=True)  # Reference to bill if converted
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    converted_by = relationship("User", foreign_keys=[converted_by_id])
    
    # Work Details
    work_performed = Column(Text, nullable=True)
    materials_used = Column(Text, nullable=True)  # JSON or text
    labor_hours = Column(Numeric(10, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WorkOrder(id={self.id}, work_order_number='{self.work_order_number}', status='{self.status}')>"


class WorkOrderItem(Base):
    """Work Order Item model for line items."""
    
    __tablename__ = "work_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    work_order = relationship("WorkOrder")
    
    item_type = Column(String(50), nullable=False)  # labor, material, service, other
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # For materials
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<WorkOrderItem(id={self.id}, work_order_id={self.work_order_id}, type='{self.item_type}')>"


"""
Broadcast Message model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class MessageType(str, enum.Enum):
    """Message type."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ANNOUNCEMENT = "announcement"


class MessagePriority(str, enum.Enum):
    """Message priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BroadcastMessage(Base):
    """Broadcast message model."""
    
    __tablename__ = "broadcast_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)  # Null for superadmin broadcasts
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.INFO)
    priority = Column(Enum(MessagePriority), default=MessagePriority.MEDIUM)
    
    # Recipients
    send_to_all = Column(Boolean, default=False)  # Send to all users
    send_to_tenant = Column(Boolean, default=False)  # Send to all users in tenant
    send_to_department = Column(String(100), nullable=True)  # Send to specific department
    send_to_users = Column(Text, nullable=True)  # JSON array of user IDs
    
    # Scheduling
    send_immediately = Column(Boolean, default=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    # Read tracking
    read_by = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BroadcastMessage(id={self.id}, title='{self.title}', type='{self.message_type}')>"


class MessageRead(Base):
    """Message read tracking."""
    
    __tablename__ = "message_reads"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("broadcast_messages.id"), nullable=False)
    message = relationship("BroadcastMessage", back_populates="read_by")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MessageRead(message_id={self.message_id}, user_id={self.user_id})>"


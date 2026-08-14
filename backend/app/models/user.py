"""
User model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles."""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    FRONTDESK = "frontdesk"
    HOUSEKEEPING = "housekeeping"
    FNB = "fnb"
    ACCOUNTANT = "accountant"
    MAINTENANCE = "maintenance"
    STAFF = "staff"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    
    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    tenant = relationship("Tenant", back_populates="users")
    
    # Permissions
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    
    # Profile
    avatar = Column(String(500), nullable=True)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    
    # Metadata
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


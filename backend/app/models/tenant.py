"""
Tenant model for multi-tenant architecture.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tenant(Base):
    """Tenant model for multi-tenant SaaS."""
    
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    subdomain = Column(String(100), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=True, unique=True, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    logo = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String(50), default="standard")
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    rooms = relationship("Room", back_populates="tenant")
    reservations = relationship("Reservation", back_populates="tenant")
    guests = relationship("Guest", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', subdomain='{self.subdomain}')>"


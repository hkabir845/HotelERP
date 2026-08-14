"""
Guest model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Guest(Base):
    """Guest model."""
    
    __tablename__ = "guests"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    mobile = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Identification
    id_type = Column(String(50), nullable=True)  # Passport, Driver License, etc.
    id_number = Column(String(100), nullable=True, index=True)
    id_expiry = Column(Date, nullable=True)
    
    # Guest Details
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    language = Column(String(50), nullable=True)
    
    # Preferences
    preferences = Column(Text, nullable=True)  # JSON string
    special_requests = Column(Text, nullable=True)
    
    # Loyalty
    loyalty_number = Column(String(50), nullable=True, index=True)
    loyalty_points = Column(Integer, default=0)
    
    # Status
    is_vip = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_visit = Column(DateTime(timezone=True), nullable=True)
    
    tenant = relationship("Tenant", back_populates="guests")
    reservations = relationship("Reservation", back_populates="guest")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Guest(id={self.id}, name='{self.full_name}', email='{self.email}')>"


"""
Frontdesk configuration models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GuestSource(Base):
    """Guest source model."""
    
    __tablename__ = "guest_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<GuestSource(id={self.id}, name='{self.name}')>"


class BookingAgent(Base):
    """Booking agent model."""
    
    __tablename__ = "booking_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    commission_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BookingAgent(id={self.id}, name='{self.name}')>"


class Company(Base):
    """Company model."""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"


class RatePlan(Base):
    """Rate plan model."""
    
    __tablename__ = "rate_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RatePlan(id={self.id}, name='{self.name}')>"


class CancellationRule(Base):
    """Cancellation rule model."""
    
    __tablename__ = "cancellation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hours_before_checkin = Column(Integer, nullable=True)  # Hours before check-in
    cancellation_charge_percentage = Column(Numeric(5, 2), nullable=True)
    cancellation_charge_amount = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CancellationRule(id={self.id}, name='{self.name}')>"


class BoardType(Base):
    """Board type model (e.g., Room Only, Breakfast, Half Board, Full Board)."""
    
    __tablename__ = "board_types"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    additional_charge = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BoardType(id={self.id}, name='{self.name}')>"


class ComplimentaryOption(Base):
    """Complimentary option model."""
    
    __tablename__ = "complimentary_options"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ComplimentaryOption(id={self.id}, name='{self.name}')>"


class RoomViewType(Base):
    """Room view type model."""
    
    __tablename__ = "room_view_types"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RoomViewType(id={self.id}, name='{self.name}')>"


class BedInfo(Base):
    """Bed info model."""
    
    __tablename__ = "bed_info"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., King, Queen, Twin, Single
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BedInfo(id={self.id}, name='{self.name}')>"


class RoomFacility(Base):
    """Room facility model."""
    
    __tablename__ = "room_facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RoomFacility(id={self.id}, name='{self.name}')>"


class RoomGroup(Base):
    """Room group model."""
    
    __tablename__ = "room_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RoomGroup(id={self.id}, name='{self.name}')>"


class ExtraChargeGroup(Base):
    """Extra charge group model."""
    
    __tablename__ = "extra_charge_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("ExtraChargeItem", back_populates="group")
    
    def __repr__(self):
        return f"<ExtraChargeGroup(id={self.id}, name='{self.name}')>"


class ExtraChargeItem(Base):
    """Extra charge item model."""
    
    __tablename__ = "extra_charge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("extra_charge_groups.id"), nullable=True)
    group = relationship("ExtraChargeGroup", back_populates="items")
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ExtraChargeItem(id={self.id}, name='{self.name}', amount={self.amount})>"


class Package(Base):
    """Package model."""
    
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Package(id={self.id}, name='{self.name}', price={self.price})>"


class AmenityDistribution(Base):
    """Amenity distribution model."""
    
    __tablename__ = "amenity_distributions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    distribution_number = Column(String(50), unique=True, nullable=False, index=True)
    
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room")
    
    distribution_date = Column(DateTime(timezone=True), nullable=False)
    distributed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    distributed_by = relationship("User")
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("AmenityDistributionItem", back_populates="distribution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AmenityDistribution(id={self.id}, distribution_number='{self.distribution_number}')>"


class AmenityDistributionItem(Base):
    """Amenity distribution item model."""
    
    __tablename__ = "amenity_distribution_items"
    
    id = Column(Integer, primary_key=True, index=True)
    distribution_id = Column(Integer, ForeignKey("amenity_distributions.id"), nullable=False)
    distribution = relationship("AmenityDistribution", back_populates="items")
    
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<AmenityDistributionItem(id={self.id}, item_name='{self.item_name}', quantity={self.quantity})>"


class WakeUpCall(Base):
    """Wake up call model."""
    
    __tablename__ = "wake_up_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room")
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    
    call_time = Column(DateTime(timezone=True), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<WakeUpCall(id={self.id}, room_id={self.room_id}, call_time='{self.call_time}')>"


class LostFound(Base):
    """Lost & Found model."""
    
    __tablename__ = "lost_found"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location_found = Column(String(200), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    room = relationship("Room")
    
    found_date = Column(DateTime(timezone=True), nullable=False)
    found_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    found_by = relationship("User", foreign_keys=[found_by_id])
    
    status = Column(String(50), default="found")  # found, claimed, disposed
    claimed_by = Column(String(200), nullable=True)
    claimed_date = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<LostFound(id={self.id}, item_name='{self.item_name}', status='{self.status}')>"


class AgentFundRequest(Base):
    """Agent fund request model."""
    
    __tablename__ = "agent_fund_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    
    agent_id = Column(Integer, ForeignKey("booking_agents.id"), nullable=False)
    agent = relationship("BookingAgent")
    
    amount = Column(Numeric(15, 2), nullable=False)
    request_date = Column(Date, nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected, paid
    
    notes = Column(Text, nullable=True)
    
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AgentFundRequest(id={self.id}, request_number='{self.request_number}', amount={self.amount})>"


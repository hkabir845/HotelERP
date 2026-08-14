"""
Billing models for Hotel & Resort operations.
Handles room charges, activities, services, group tours, etc.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class BillStatus(str, enum.Enum):
    """Bill status."""
    DRAFT = "draft"
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class BillType(str, enum.Enum):
    """Bill type."""
    ROOM_CHARGE = "room_charge"
    FOOD_BEVERAGE = "food_beverage"
    ACTIVITY = "activity"
    SERVICE = "service"
    GROUP_TOUR = "group_tour"
    MISC = "misc"
    CONSOLIDATED = "consolidated"  # Final bill at checkout


class PaymentMethod(str, enum.Enum):
    """Payment method."""
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CREDIT = "credit"
    WALLET = "wallet"
    OTHER = "other"


class BillingItemCategory(Base):
    """Billing item category."""
    
    __tablename__ = "billing_item_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category_type = Column(String(50), nullable=True)  # room, activity, service, food, etc.
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("BillingItem", back_populates="category")
    
    def __repr__(self):
        return f"<BillingItemCategory(id={self.id}, name='{self.name}')>"


class BillingItem(Base):
    """Billing item - charges that can be added to bills."""
    
    __tablename__ = "billing_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    category_id = Column(Integer, ForeignKey("billing_item_categories.id"), nullable=True)
    category = relationship("BillingItemCategory", back_populates="items")
    
    # Pricing
    base_price = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)  # Percentage
    service_charge_rate = Column(Numeric(5, 2), default=0)  # Percentage
    
    # Unit
    unit = Column(String(50), nullable=True)  # per night, per hour, per person, etc.
    
    # Applicability
    applicable_to = Column(String(50), nullable=True)  # room, guest, group, activity, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bill_items = relationship("BillItem", back_populates="billing_item")
    
    def __repr__(self):
        return f"<BillingItem(id={self.id}, item_code='{self.item_code}', name='{self.name}')>"


class Activity(Base):
    """Resort activity model (e.g., spa, gym, pool, tours, excursions)."""
    
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    activity_code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Spa, Fitness, Recreation, Tour, etc.
    
    # Pricing
    price_per_person = Column(Numeric(15, 2), nullable=True)
    price_per_group = Column(Numeric(15, 2), nullable=True)
    duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Capacity
    max_participants = Column(Integer, nullable=True)
    min_participants = Column(Integer, default=1)
    
    # Availability
    is_active = Column(Boolean, default=True)
    available_days = Column(String(50), nullable=True)  # JSON or comma-separated
    available_times = Column(String(100), nullable=True)  # JSON or time range
    
    # Metadata
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    bookings = relationship("ActivityBooking", back_populates="activity")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, activity_code='{self.activity_code}', name='{self.name}')>"


class ActivityBooking(Base):
    """Activity booking model."""
    
    __tablename__ = "activity_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    activity = relationship("Activity", back_populates="bookings")
    
    # Guest/Reservation
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    
    # Booking Details
    booking_date = Column(DateTime(timezone=True), nullable=False)
    activity_date = Column(DateTime(timezone=True), nullable=False)
    number_of_participants = Column(Integer, default=1)
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="confirmed")  # confirmed, completed, cancelled
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<ActivityBooking(id={self.id}, booking_number='{self.booking_number}')>"


class GroupTour(Base):
    """Group tour model."""
    
    __tablename__ = "group_tours"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    tour_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Tour Details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    destination = Column(String(200), nullable=True)
    
    # Dates
    tour_date = Column(DateTime(timezone=True), nullable=False)
    duration_days = Column(Integer, default=1)
    
    # Participants
    group_leader_name = Column(String(200), nullable=True)
    group_leader_phone = Column(String(50), nullable=True)
    number_of_guests = Column(Integer, default=1)
    
    # Pricing
    price_per_person = Column(Numeric(15, 2), nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="confirmed")  # confirmed, in_progress, completed, cancelled
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<GroupTour(id={self.id}, tour_number='{self.tour_number}', name='{self.name}')>"


class Bill(Base):
    """Bill model - Consolidated billing for guests/reservations."""
    
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    bill_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Related Entities
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    
    # Bill Type
    bill_type = Column(Enum(BillType), nullable=False)
    
    # Dates
    bill_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=True)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    service_charge = Column(Numeric(15, 2), default=0)
    discount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    # Currency
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True)
    currency_code = Column(String(3), nullable=True)  # Denormalized for performance
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    
    # Status
    status = Column(Enum(BillStatus), default=BillStatus.PENDING)
    
    # Notes
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("BillPayment", back_populates="bill", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bill(id={self.id}, bill_number='{self.bill_number}', total={self.total_amount})>"


class BillItem(Base):
    """Bill line item."""
    
    __tablename__ = "bill_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    bill = relationship("Bill", back_populates="items")
    
    billing_item_id = Column(Integer, ForeignKey("billing_items.id"), nullable=True)
    billing_item = relationship("BillingItem", back_populates="bill_items")
    
    # Item Details
    description = Column(Text, nullable=False)
    item_type = Column(String(50), nullable=True)  # room, food, activity, service, etc.
    
    # Quantity & Pricing
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    service_charge_rate = Column(Numeric(5, 2), default=0)
    service_charge_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Related entities
    related_type = Column(String(50), nullable=True)  # reservation, order, activity, work_order, etc.
    related_id = Column(Integer, nullable=True)
    
    # Dates
    charge_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<BillItem(id={self.id}, bill_id={self.bill_id}, description='{self.description[:30]}...')>"


class BillPayment(Base):
    """Bill payment model."""
    
    __tablename__ = "bill_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    bill = relationship("Bill", back_populates="payments")
    
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_reference = Column(String(100), nullable=True)  # Check number, transaction ID, etc.
    
    # Currency
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True)
    currency_code = Column(String(3), nullable=True)
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    amount_in_base_currency = Column(Numeric(15, 2), nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<BillPayment(id={self.id}, payment_number='{self.payment_number}', amount={self.amount})>"


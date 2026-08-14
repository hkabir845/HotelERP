"""
Inventory Management models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RequisitionStatus(str, enum.Enum):
    """Requisition status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FULFILLED = "fulfilled"


class PurchaseStatus(str, enum.Enum):
    """Purchase status."""
    DRAFT = "draft"
    PENDING = "pending"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Requisition(Base):
    """Requisition model."""
    
    __tablename__ = "requisitions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    requisition_number = Column(String(50), unique=True, nullable=False, index=True)
    
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    
    department = Column(String(100), nullable=True)
    status = Column(Enum(RequisitionStatus), default=RequisitionStatus.PENDING)
    
    requested_date = Column(Date, nullable=False)
    required_date = Column(Date, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("RequisitionItem", back_populates="requisition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Requisition(id={self.id}, requisition_number='{self.requisition_number}', status='{self.status}')>"


class RequisitionItem(Base):
    """Requisition item model."""
    
    __tablename__ = "requisition_items"
    
    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("requisitions.id"), nullable=False)
    requisition = relationship("Requisition", back_populates="items")
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    item = relationship("InventoryItem")
    
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<RequisitionItem(id={self.id}, requisition_id={self.requisition_id}, quantity={self.quantity})>"


class InventoryItem(Base):
    """Inventory item model."""
    
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    category_id = Column(Integer, ForeignKey("inventory_categories.id"), nullable=True)
    category = relationship("InventoryCategory", back_populates="items")
    
    unit = Column(String(50), nullable=False)
    
    # Stock
    current_stock = Column(Numeric(10, 2), default=0)
    min_stock_level = Column(Numeric(10, 2), default=0)
    max_stock_level = Column(Numeric(10, 2), nullable=True)
    
    # Pricing
    cost_price = Column(Numeric(10, 2), nullable=True)
    selling_price = Column(Numeric(10, 2), nullable=True)
    
    # Warehouse
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    warehouse = relationship("Warehouse", back_populates="items")
    
    # Supplier
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier = relationship("Supplier")
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, item_code='{self.item_code}', name='{self.name}')>"


class InventoryCategory(Base):
    """Inventory category model."""
    
    __tablename__ = "inventory_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("InventoryItem", back_populates="category")
    
    def __repr__(self):
        return f"<InventoryCategory(id={self.id}, name='{self.name}')>"


class Warehouse(Base):
    """Warehouse model."""
    
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("InventoryItem", back_populates="warehouse")
    transfers = relationship("WarehouseTransfer", foreign_keys="WarehouseTransfer.from_warehouse_id", back_populates="from_warehouse")
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, name='{self.name}')>"


class Supplier(Base):
    """Supplier model."""
    
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    purchases = relationship("Purchase", back_populates="supplier")
    payments = relationship("SupplierPayment", back_populates="supplier", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class Purchase(Base):
    """Purchase model."""
    
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    purchase_number = Column(String(50), unique=True, nullable=False, index=True)
    
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="purchases")
    
    purchase_date = Column(Date, nullable=False)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.DRAFT)
    
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Purchase(id={self.id}, purchase_number='{self.purchase_number}', status='{self.status}')>"


class PurchaseItem(Base):
    """Purchase item model."""
    
    __tablename__ = "purchase_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    purchase = relationship("Purchase", back_populates="items")
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    item = relationship("InventoryItem")
    
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f"<PurchaseItem(id={self.id}, purchase_id={self.purchase_id}, quantity={self.quantity})>"


class WarehouseTransfer(Base):
    """Warehouse transfer model."""
    
    __tablename__ = "warehouse_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    transfer_number = Column(String(50), unique=True, nullable=False, index=True)
    
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    from_warehouse = relationship("Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id])
    
    transfer_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    items = relationship("WarehouseTransferItem", back_populates="transfer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WarehouseTransfer(id={self.id}, transfer_number='{self.transfer_number}')>"


class WarehouseTransferItem(Base):
    """Warehouse transfer item model."""
    
    __tablename__ = "warehouse_transfer_items"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("warehouse_transfers.id"), nullable=False)
    transfer = relationship("WarehouseTransfer", back_populates="items")
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    item = relationship("InventoryItem")
    
    quantity = Column(Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f"<WarehouseTransferItem(id={self.id}, transfer_id={self.transfer_id}, quantity={self.quantity})>"


class StockAdjustment(Base):
    """Stock adjustment model."""
    
    __tablename__ = "stock_adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    adjustment_number = Column(String(50), unique=True, nullable=False, index=True)
    
    adjustment_type = Column(String(20), nullable=False)  # add, remove
    adjustment_date = Column(Date, nullable=False)
    
    reason = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    items = relationship("StockAdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StockAdjustment(id={self.id}, adjustment_number='{self.adjustment_number}', type='{self.adjustment_type}')>"


class StockAdjustmentItem(Base):
    """Stock adjustment item model."""
    
    __tablename__ = "stock_adjustment_items"
    
    id = Column(Integer, primary_key=True, index=True)
    adjustment_id = Column(Integer, ForeignKey("stock_adjustments.id"), nullable=False)
    adjustment = relationship("StockAdjustment", back_populates="items")
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    item = relationship("InventoryItem")
    
    quantity = Column(Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f"<StockAdjustmentItem(id={self.id}, adjustment_id={self.adjustment_id}, quantity={self.quantity})>"


class SupplierPayment(Base):
    """Supplier payment model."""
    
    __tablename__ = "supplier_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="payments")
    
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)
    reference = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<SupplierPayment(id={self.id}, supplier_id={self.supplier_id}, amount={self.amount})>"


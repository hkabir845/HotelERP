"""
Currency and Multi-Currency Support models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Currency(Base):
    """Currency model for multi-currency support."""
    
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)  # NULL for global currencies
    
    code = Column(String(3), nullable=False, unique=True, index=True)  # USD, EUR, BDT, etc.
    name = Column(String(100), nullable=False)  # US Dollar, Euro, Bangladeshi Taka
    symbol = Column(String(10), nullable=False)  # $, €, ৳
    
    # Exchange rates (relative to base currency)
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    is_base_currency = Column(Boolean, default=False)
    
    # Formatting
    decimal_places = Column(Integer, default=2)
    symbol_position = Column(String(10), default="before")  # before, after
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Currency(id={self.id}, code='{self.code}', name='{self.name}')>"


class CurrencyExchangeRate(Base):
    """Currency exchange rate history."""
    
    __tablename__ = "currency_exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    
    from_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    from_currency = relationship("Currency", foreign_keys=[from_currency_id])
    
    to_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    to_currency = relationship("Currency", foreign_keys=[to_currency_id])
    
    rate = Column(Numeric(15, 6), nullable=False)
    effective_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<CurrencyExchangeRate(id={self.id}, from={self.from_currency_id}, to={self.to_currency_id}, rate={self.rate})>"


class TenantCurrency(Base):
    """Tenant currency settings."""
    
    __tablename__ = "tenant_currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True, index=True)
    
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    base_currency = relationship("Currency", foreign_keys=[base_currency_id])
    
    # Allowed currencies for this tenant
    allowed_currency_ids = Column(Text, nullable=True)  # JSON array of currency IDs
    
    # Auto-update exchange rates
    auto_update_rates = Column(Boolean, default=False)
    last_rate_update = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TenantCurrency(id={self.id}, tenant_id={self.tenant_id}, base_currency_id={self.base_currency_id})>"


"""
Full-fledged Accounting System models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AccountType(str, enum.Enum):
    """Account type."""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class TransactionType(str, enum.Enum):
    """Transaction type."""
    DEBIT = "debit"
    CREDIT = "credit"


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ChartOfAccount(Base):
    """Chart of Accounts model."""
    
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    account_code = Column(String(50), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="sub_accounts")
    
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_system_account = Column(Boolean, default=False)  # Cannot be deleted
    
    # Opening balance
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    transactions = relationship("AccountTransaction", back_populates="account")
    
    def __repr__(self):
        return f"<ChartOfAccount(id={self.id}, code='{self.account_code}', name='{self.account_name}')>"


class JournalEntry(Base):
    """Journal Entry model."""
    
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    
    entry_date = Column(Date, nullable=False, index=True)
    reference = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Totals
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    
    # Status
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    posted_by = relationship("User", foreign_keys=[posted_by_id])
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    transactions = relationship("AccountTransaction", back_populates="journal_entry", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JournalEntry(id={self.id}, entry_number='{self.entry_number}', date='{self.entry_date}')>"


class AccountTransaction(Base):
    """Account Transaction model."""
    
    __tablename__ = "account_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    journal_entry = relationship("JournalEntry", back_populates="transactions")
    
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    account = relationship("ChartOfAccount", back_populates="transactions")
    
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    # Related entities
    related_type = Column(String(50), nullable=True)  # reservation, order, payment, etc.
    related_id = Column(Integer, nullable=True)
    
    # Metadata
    transaction_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AccountTransaction(id={self.id}, account_id={self.account_id}, type='{self.transaction_type}', amount={self.amount})>"


class AccountsPayable(Base):
    """Accounts Payable model."""
    
    __tablename__ = "accounts_payable"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    
    vendor_name = Column(String(200), nullable=False)
    vendor_id = Column(Integer, nullable=True)  # If vendor is in system
    
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    
    amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Accounting
    expense_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    expense_account = relationship("ChartOfAccount", foreign_keys=[expense_account_id])
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    payments = relationship("APPayment", back_populates="accounts_payable", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AccountsPayable(id={self.id}, invoice_number='{self.invoice_number}', balance={self.balance})>"


class APPayment(Base):
    """Accounts Payable Payment model."""
    
    __tablename__ = "ap_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    accounts_payable_id = Column(Integer, ForeignKey("accounts_payable.id"), nullable=False)
    accounts_payable = relationship("AccountsPayable", back_populates="payments")
    
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)  # Cash, Bank Transfer, Check, etc.
    reference = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<APPayment(id={self.id}, amount={self.amount}, date='{self.payment_date}')>"


class AccountsReceivable(Base):
    """Accounts Receivable model."""
    
    __tablename__ = "accounts_receivable"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    
    customer_name = Column(String(200), nullable=False)
    customer_id = Column(Integer, nullable=True)  # If customer is in system
    
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    
    amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Related reservation/order
    related_type = Column(String(50), nullable=True)
    related_id = Column(Integer, nullable=True)
    
    # Accounting
    revenue_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    revenue_account = relationship("ChartOfAccount", foreign_keys=[revenue_account_id])
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    payments = relationship("ARPayment", back_populates="accounts_receivable", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AccountsReceivable(id={self.id}, invoice_number='{self.invoice_number}', balance={self.balance})>"


class ARPayment(Base):
    """Accounts Receivable Payment model."""
    
    __tablename__ = "ar_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    accounts_receivable_id = Column(Integer, ForeignKey("accounts_receivable.id"), nullable=False)
    accounts_receivable = relationship("AccountsReceivable", back_populates="payments")
    
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)
    reference = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<ARPayment(id={self.id}, amount={self.amount}, date='{self.payment_date}')>"


class Budget(Base):
    """Budget model."""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    account = relationship("ChartOfAccount")
    
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    budgeted_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', period='{self.period_start} to {self.period_end}')>"


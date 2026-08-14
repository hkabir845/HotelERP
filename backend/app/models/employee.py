"""
Employee and Payroll models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class EmploymentStatus(str, enum.Enum):
    """Employment status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class PayrollStatus(str, enum.Enum):
    """Payroll status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class Employee(Base):
    """Employee model."""
    
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Link to User account
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    user = relationship("User", foreign_keys=[user_id])
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Employment Details
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    employment_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    
    # Dates
    date_of_birth = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    
    # Status
    status = Column(Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE)
    
    # Payroll Info
    salary = Column(Numeric(15, 2), nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    pay_frequency = Column(String(20), nullable=True)  # weekly, bi-weekly, monthly
    bank_account = Column(String(100), nullable=True)
    bank_name = Column(String(200), nullable=True)
    tax_id = Column(String(50), nullable=True)
    
    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    payroll_records = relationship("Payroll", back_populates="employee")
    attendance_records = relationship("Attendance", back_populates="employee")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_number='{self.employee_number}', name='{self.full_name}')>"


class Attendance(Base):
    """Employee attendance model."""
    
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="attendance_records")
    
    attendance_date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    
    hours_worked = Column(Numeric(5, 2), default=0)
    overtime_hours = Column(Numeric(5, 2), default=0)
    
    status = Column(String(50), nullable=True)  # present, absent, late, half_day, leave
    leave_type = Column(String(50), nullable=True)  # sick, vacation, personal, etc.
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date='{self.attendance_date}')>"


class Payroll(Base):
    """Payroll model."""
    
    __tablename__ = "payroll"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    payroll_number = Column(String(50), unique=True, nullable=False, index=True)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="payroll_records")
    
    # Period
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Earnings
    base_salary = Column(Numeric(15, 2), default=0)
    hours_worked = Column(Numeric(5, 2), default=0)
    hourly_rate = Column(Numeric(10, 2), default=0)
    overtime_hours = Column(Numeric(5, 2), default=0)
    overtime_rate = Column(Numeric(10, 2), default=0)
    overtime_amount = Column(Numeric(15, 2), default=0)
    bonus = Column(Numeric(15, 2), default=0)
    allowances = Column(Numeric(15, 2), default=0)
    gross_pay = Column(Numeric(15, 2), nullable=False)
    
    # Deductions
    tax = Column(Numeric(15, 2), default=0)
    social_security = Column(Numeric(15, 2), default=0)
    health_insurance = Column(Numeric(15, 2), default=0)
    other_deductions = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    
    # Net Pay
    net_pay = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(Enum(PayrollStatus), default=PayrollStatus.DRAFT)
    
    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment
    paid_at = Column(DateTime(timezone=True), nullable=True)
    paid_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    paid_by = relationship("User", foreign_keys=[paid_by_id])
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<Payroll(id={self.id}, payroll_number='{self.payroll_number}', net_pay={self.net_pay})>"


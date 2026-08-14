"""Employee and Payroll models."""
from django.db import models


class EmploymentStatus(models.TextChoices):
    """Employment status."""

    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    TERMINATED = 'terminated', 'Terminated'
    ON_LEAVE = 'on_leave', 'On Leave'


class PayrollStatus(models.TextChoices):
    """Payroll status."""

    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    PAID = 'paid', 'Paid'
    CANCELLED = 'cancelled', 'Cancelled'


class Employee(models.Model):
    """Employee model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='employees',
        db_index=True,
    )
    employee_number = models.CharField(max_length=50, unique=True, db_index=True)

    user = models.OneToOneField(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)

    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    work_shift = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    employment_type = models.CharField(max_length=50, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )

    salary = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pay_frequency = models.CharField(max_length=20, null=True, blank=True)
    bank_account = models.CharField(max_length=100, null=True, blank=True)
    bank_name = models.CharField(max_length=200, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)

    emergency_contact_name = models.CharField(max_length=200, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=50, null=True, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'employees'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return (
            f"Employee(id={self.id}, employee_number='{self.employee_number}', "
            f"name='{self.full_name}')"
        )


class Attendance(models.Model):
    """Employee attendance model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        db_index=True,
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )

    attendance_date = models.DateField(db_index=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_minutes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    late_fine = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=50, null=True, blank=True)
    leave_type = models.CharField(max_length=50, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'

    def __str__(self):
        return f"Attendance(id={self.id}, employee_id={self.employee_id}, date='{self.attendance_date}')"


class Payroll(models.Model):
    """Payroll model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='payroll_records',
        db_index=True,
    )
    payroll_number = models.CharField(max_length=50, unique=True, db_index=True)

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payroll_records',
    )

    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    pay_date = models.DateField()

    base_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=15, decimal_places=2)

    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    social_security = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    health_insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    net_pay = models.DecimalField(max_digits=15, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PayrollStatus.choices,
        default=PayrollStatus.DRAFT,
    )

    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_approved',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_paid',
    )
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)

    accrual_journal = models.ForeignKey(
        'JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_accruals',
    )
    payment_journal = models.ForeignKey(
        'JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_payments',
    )

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_created',
    )

    class Meta:
        db_table = 'payroll'

    def __str__(self):
        return f"Payroll(id={self.id}, payroll_number='{self.payroll_number}', net_pay={self.net_pay})"

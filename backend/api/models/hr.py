"""HR masters, leave, loans, salary structure, and settings."""
from django.db import models


class HrNamed(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name='{self.name}')"


class HrBranch(HrNamed):
    class Meta:
        db_table = 'hr_branches'


class HrDepartment(HrNamed):
    class Meta:
        db_table = 'hr_departments'


class HrDesignation(HrNamed):
    class Meta:
        db_table = 'hr_designations'


class HrWorkShift(HrNamed):
    start_time = models.CharField(max_length=8, blank=True, default='09:00')
    end_time = models.CharField(max_length=8, blank=True, default='18:00')
    grace_minutes = models.PositiveIntegerField(default=15)

    class Meta:
        db_table = 'hr_work_shifts'


class HrLeaveType(HrNamed):
    days_per_year = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_leave_types'


class HrHoliday(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='hr_holidays', db_index=True)
    name = models.CharField(max_length=200)
    holiday_date = models.DateField(db_index=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_holidays'
        ordering = ['holiday_date']


class HrSalaryStructure(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='hr_salary_structures')
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, related_name='salary_structure')
    basic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    house_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conveyance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_salary_structures'

    @property
    def gross(self):
        return self.basic + self.house_rent + self.medical + self.conveyance + self.other_allowance


class HrLeaveRequest(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='hr_leave_requests', db_index=True)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(
        HrLeaveType, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests'
    )
    date_from = models.DateField()
    date_to = models.DateField()
    days = models.DecimalField(max_digits=6, decimal_places=1, default=1)
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, default='pending', db_index=True)
    decided_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_leave_decisions'
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_leave_requests'
        ordering = ['-id']


class HrLoan(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='hr_loans', db_index=True)
    number = models.CharField(max_length=40, db_index=True)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    installments = models.PositiveIntegerField(default=1)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    request_date = models.DateField()
    purpose = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_loans'
        ordering = ['-id']


class HrSettings(models.Model):
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE, related_name='hr_settings')
    work_start = models.CharField(max_length=8, default='09:00')
    work_end = models.CharField(max_length=8, default='18:00')
    late_grace_minutes = models.PositiveIntegerField(default=15)
    late_fine_amount = models.DecimalField(max_digits=12, decimal_places=2, default=50)
    overtime_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_settings'

"""Asset & Maintenance models."""
from django.db import models


class AssetStatus(models.TextChoices):
    """Asset status."""

    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    DISPOSED = 'disposed', 'Disposed'
    UNDER_MAINTENANCE = 'under_maintenance', 'Under Maintenance'


class MaintenanceStatus(models.TextChoices):
    """Maintenance status."""

    PENDING = 'pending', 'Pending'
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class MaintenanceType(models.TextChoices):
    """Maintenance type."""

    PREVENTIVE = 'preventive', 'Preventive'
    CORRECTIVE = 'corrective', 'Corrective'
    EMERGENCY = 'emergency', 'Emergency'
    INSPECTION = 'inspection', 'Inspection'


class AssetCategory(models.Model):
    """Asset category model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='asset_categories',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'asset_categories'

    def __str__(self):
        return f"AssetCategory(id={self.id}, name='{self.name}')"


class AssetType(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='asset_types', db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_types'


class AssetVendor(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='asset_vendors', db_index=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    address = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_vendors'


class AssetVendorContract(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='asset_vendor_contracts', db_index=True)
    vendor = models.ForeignKey(AssetVendor, on_delete=models.CASCADE, related_name='contracts')
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_vendor_contracts'


class Asset(models.Model):
    """Asset model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='assets',
        db_index=True,
    )

    asset_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.CASCADE,
        related_name='assets',
    )

    location = models.CharField(max_length=200, null=True, blank=True)
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
    )

    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)

    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    depreciation_method = models.CharField(max_length=50, null=True, blank=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.ACTIVE,
    )
    condition = models.CharField(max_length=50, null=True, blank=True)

    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_due = models.DateField(null=True, blank=True)

    serial_number = models.CharField(max_length=100, null=True, blank=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets_created',
    )

    class Meta:
        db_table = 'assets'

    def __str__(self):
        return f"Asset(id={self.id}, asset_code='{self.asset_code}', name='{self.name}')"


class MaintenanceRequest(models.Model):
    """Maintenance request model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        db_index=True,
    )
    request_number = models.CharField(max_length=50, unique=True, db_index=True)

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests',
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests',
    )

    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING,
    )
    priority = models.CharField(max_length=20, default='medium')

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    reported_issue = models.TextField(null=True, blank=True)

    requested_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests_requested',
    )
    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests_assigned',
    )

    requested_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    work_performed = models.TextField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    parts_used = models.TextField(null=True, blank=True)

    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests_approved',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'maintenance_requests'

    def __str__(self):
        return (
            f"MaintenanceRequest(id={self.id}, request_number='{self.request_number}', "
            f"status='{self.status}')"
        )


class MaintenanceSchedule(models.Model):
    """Preventive maintenance schedule model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='maintenance_schedules',
        db_index=True,
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='maintenance_schedules',
    )

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    frequency_type = models.CharField(max_length=20)
    frequency_value = models.IntegerField(default=1)
    next_due_date = models.DateField(db_index=True)
    last_performed = models.DateField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_schedules_assigned',
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_schedules_created',
    )

    class Meta:
        db_table = 'maintenance_schedules'

    def __str__(self):
        return (
            f"MaintenanceSchedule(id={self.id}, asset_id={self.asset_id}, "
            f"next_due='{self.next_due_date}')"
        )

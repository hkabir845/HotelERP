"""Work Order models - Can be converted to bills after approval."""
from django.db import models


class WorkOrderStatus(models.TextChoices):
    """Work order status."""

    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    CONVERTED_TO_BILL = 'converted_to_bill', 'Converted to Bill'


class WorkOrderPriority(models.TextChoices):
    """Work order priority."""

    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class WorkOrder(models.Model):
    """Work Order model - Can be converted to bill after approval."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='work_orders',
        db_index=True,
    )
    work_order_number = models.CharField(max_length=50, unique=True, db_index=True)

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    work_type = models.CharField(max_length=100, null=True, blank=True)

    location = models.CharField(max_length=200, null=True, blank=True)
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
    )
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
    )

    status = models.CharField(
        max_length=20,
        choices=WorkOrderStatus.choices,
        default=WorkOrderStatus.DRAFT,
    )
    priority = models.CharField(
        max_length=20,
        choices=WorkOrderPriority.choices,
        default=WorkOrderPriority.MEDIUM,
    )

    requested_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders_requested',
    )
    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders_assigned',
    )

    requested_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders_approved',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(null=True, blank=True)

    converted_to_bill = models.BooleanField(default=False)
    bill_id = models.IntegerField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    converted_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders_converted',
    )

    work_performed = models.TextField(null=True, blank=True)
    materials_used = models.TextField(null=True, blank=True)
    labor_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'work_orders'

    def __str__(self):
        return (
            f"WorkOrder(id={self.id}, work_order_number='{self.work_order_number}', "
            f"status='{self.status}')"
        )


class WorkOrderItem(models.Model):
    """Work Order Item model for line items."""

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )

    item_type = models.CharField(max_length=50)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    inventory_item = models.ForeignKey(
        'InventoryItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_items',
    )

    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'work_order_items'

    def __str__(self):
        return f"WorkOrderItem(id={self.id}, work_order_id={self.work_order_id}, type='{self.item_type}')"

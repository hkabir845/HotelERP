"""Inventory Management models."""
from django.db import models


class RequisitionStatus(models.TextChoices):
    """Requisition status."""

    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    FULFILLED = 'fulfilled', 'Fulfilled'


class PurchaseStatus(models.TextChoices):
    """Purchase status."""

    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    RECEIVED = 'received', 'Received'
    CANCELLED = 'cancelled', 'Cancelled'


class InventoryCategory(models.Model):
    """Inventory category model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='inventory_categories',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'inventory_categories'

    def __str__(self):
        return f"InventoryCategory(id={self.id}, name='{self.name}')"


class InventoryUnit(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='inventory_units',
        db_index=True,
    )
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'inventory_units'

    def __str__(self):
        return f"InventoryUnit(id={self.id}, name='{self.name}')"


class Warehouse(models.Model):
    """Warehouse model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='warehouses',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'warehouses'

    def __str__(self):
        return f"Warehouse(id={self.id}, name='{self.name}')"


class Supplier(models.Model):
    """Supplier model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='suppliers',
        db_index=True,
    )

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'suppliers'

    def __str__(self):
        return f"Supplier(id={self.id}, name='{self.name}')"


class InventoryItem(models.Model):
    """Inventory item model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        db_index=True,
    )

    item_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )

    unit = models.CharField(max_length=50)

    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_stock_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'inventory_items'

    def __str__(self):
        return f"InventoryItem(id={self.id}, item_code='{self.item_code}', name='{self.name}')"


class InventoryStock(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='inventory_stocks',
        db_index=True,
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='stocks',
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stocks',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'inventory_stocks'
        unique_together = ('item', 'warehouse')


class InventoryMovement(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='inventory_movements',
        db_index=True,
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='movements',
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='movements',
    )
    movement_date = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ref_type = models.CharField(max_length=40)
    ref_id = models.IntegerField(null=True, blank=True)
    ref_number = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements',
    )

    class Meta:
        db_table = 'inventory_movements'


class Requisition(models.Model):
    """Requisition model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='requisitions',
        db_index=True,
    )
    requisition_number = models.CharField(max_length=50, unique=True, db_index=True)

    requested_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='requisitions_requested',
    )

    department = models.CharField(max_length=100, null=True, blank=True)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisitions',
    )
    status = models.CharField(
        max_length=20,
        choices=RequisitionStatus.choices,
        default=RequisitionStatus.PENDING,
    )

    requested_date = models.DateField()
    required_date = models.DateField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisitions_approved',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'requisitions'

    def __str__(self):
        return (
            f"Requisition(id={self.id}, requisition_number='{self.requisition_number}', "
            f"status='{self.status}')"
        )


class RequisitionItem(models.Model):
    """Requisition item model."""

    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='requisition_items',
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'requisition_items'

    def __str__(self):
        return (
            f"RequisitionItem(id={self.id}, requisition_id={self.requisition_id}, "
            f"quantity={self.quantity})"
        )


class Purchase(models.Model):
    """Purchase model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='purchases',
        db_index=True,
    )
    purchase_number = models.CharField(max_length=50, unique=True, db_index=True)

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchases',
    )

    purchase_date = models.DateField()
    is_return = models.BooleanField(default=False)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases',
    )
    status = models.CharField(
        max_length=20,
        choices=PurchaseStatus.choices,
        default=PurchaseStatus.DRAFT,
    )

    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    notes = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases_created',
    )

    class Meta:
        db_table = 'purchases'

    def __str__(self):
        return f"Purchase(id={self.id}, purchase_number='{self.purchase_number}', status='{self.status}')"


class PurchaseItem(models.Model):
    """Purchase item model."""

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='purchase_items',
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'purchase_items'

    def __str__(self):
        return f"PurchaseItem(id={self.id}, purchase_id={self.purchase_id}, quantity={self.quantity})"


class WarehouseTransfer(models.Model):
    """Warehouse transfer model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='warehouse_transfers',
        db_index=True,
    )
    transfer_number = models.CharField(max_length=50, unique=True, db_index=True)

    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='transfers',
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
    )

    transfer_date = models.DateField()
    status = models.CharField(max_length=20, default='draft')
    notes = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warehouse_transfers_created',
    )

    class Meta:
        db_table = 'warehouse_transfers'

    def __str__(self):
        return f"WarehouseTransfer(id={self.id}, transfer_number='{self.transfer_number}')"


class WarehouseTransferItem(models.Model):
    """Warehouse transfer item model."""

    transfer = models.ForeignKey(
        WarehouseTransfer,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='warehouse_transfer_items',
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'warehouse_transfer_items'

    def __str__(self):
        return (
            f"WarehouseTransferItem(id={self.id}, transfer_id={self.transfer_id}, "
            f"quantity={self.quantity})"
        )


class StockAdjustment(models.Model):
    """Stock adjustment model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='stock_adjustments',
        db_index=True,
    )
    adjustment_number = models.CharField(max_length=50, unique=True, db_index=True)

    adjustment_type = models.CharField(max_length=20)
    adjustment_date = models.DateField()
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_adjustments',
    )
    status = models.CharField(max_length=20, default='draft')

    reason = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_adjustments_created',
    )

    class Meta:
        db_table = 'stock_adjustments'

    def __str__(self):
        return (
            f"StockAdjustment(id={self.id}, adjustment_number='{self.adjustment_number}', "
            f"type='{self.adjustment_type}')"
        )


class StockAdjustmentItem(models.Model):
    """Stock adjustment item model."""

    adjustment = models.ForeignKey(
        StockAdjustment,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='stock_adjustment_items',
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'stock_adjustment_items'

    def __str__(self):
        return (
            f"StockAdjustmentItem(id={self.id}, adjustment_id={self.adjustment_id}, "
            f"quantity={self.quantity})"
        )


class StockConsumption(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='stock_consumptions',
        db_index=True,
    )
    consumption_number = models.CharField(max_length=50, unique=True, db_index=True)
    kind = models.CharField(max_length=30)
    consumption_date = models.DateField()
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consumptions',
    )
    revenue_center = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='draft')
    notes = models.TextField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_consumptions_created',
    )

    class Meta:
        db_table = 'stock_consumptions'


class StockConsumptionItem(models.Model):
    consumption = models.ForeignKey(
        StockConsumption,
        on_delete=models.CASCADE,
        related_name='items',
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='consumption_items',
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'stock_consumption_items'


class SupplierPayment(models.Model):
    """Supplier payment model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='supplier_payments',
        db_index=True,
        null=True,
        blank=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='payments',
    )

    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_payments_created',
    )

    class Meta:
        db_table = 'supplier_payments'

    def __str__(self):
        return f"SupplierPayment(id={self.id}, supplier_id={self.supplier_id}, amount={self.amount})"

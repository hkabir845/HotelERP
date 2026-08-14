"""Billing models for Hotel & Resort operations."""
from django.db import models


class BillStatus(models.TextChoices):
    """Bill status."""

    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    PARTIAL = 'partial', 'Partial'
    PAID = 'paid', 'Paid'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class BillType(models.TextChoices):
    """Bill type."""

    ROOM_CHARGE = 'room_charge', 'Room Charge'
    FOOD_BEVERAGE = 'food_beverage', 'Food & Beverage'
    ACTIVITY = 'activity', 'Activity'
    SERVICE = 'service', 'Service'
    GROUP_TOUR = 'group_tour', 'Group Tour'
    MISC = 'misc', 'Misc'
    CONSOLIDATED = 'consolidated', 'Consolidated'


class PaymentMethod(models.TextChoices):
    """Payment method."""

    CASH = 'cash', 'Cash'
    CARD = 'card', 'Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CHECK = 'check', 'Check'
    CREDIT = 'credit', 'Credit'
    WALLET = 'wallet', 'Wallet'
    OTHER = 'other', 'Other'


class BillingItemCategory(models.Model):
    """Billing item category."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='billing_item_categories',
        db_index=True,
    )

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category_type = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'billing_item_categories'
        verbose_name_plural = 'billing item categories'

    def __str__(self):
        return f"BillingItemCategory(id={self.id}, name='{self.name}')"


class BillingItem(models.Model):
    """Billing item - charges that can be added to bills."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='billing_items',
        db_index=True,
    )

    item_code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        BillingItemCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )

    base_price = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    unit = models.CharField(max_length=50, null=True, blank=True)
    applicable_to = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'billing_items'

    def __str__(self):
        return f"BillingItem(id={self.id}, item_code='{self.item_code}', name='{self.name}')"


class Activity(models.Model):
    """Resort activity model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='activities',
        db_index=True,
    )

    activity_code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    price_per_person = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_per_group = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    max_participants = models.IntegerField(null=True, blank=True)
    min_participants = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)
    available_days = models.CharField(max_length=50, null=True, blank=True)
    available_times = models.CharField(max_length=100, null=True, blank=True)

    location = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'activities'
        verbose_name_plural = 'activities'

    def __str__(self):
        return f"Activity(id={self.id}, activity_code='{self.activity_code}', name='{self.name}')"


class ActivityBooking(models.Model):
    """Activity booking model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='activity_bookings',
        db_index=True,
    )
    booking_number = models.CharField(max_length=50, unique=True, db_index=True)

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='bookings',
    )

    guest = models.ForeignKey(
        'Guest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_bookings',
    )
    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_bookings',
    )

    booking_date = models.DateTimeField()
    activity_date = models.DateTimeField()
    number_of_participants = models.IntegerField(default=1)

    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    status = models.CharField(max_length=50, default='confirmed')

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_bookings_created',
    )

    class Meta:
        db_table = 'activity_bookings'

    def __str__(self):
        return f"ActivityBooking(id={self.id}, booking_number='{self.booking_number}')"


class GroupTour(models.Model):
    """Group tour model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='group_tours',
        db_index=True,
    )
    tour_number = models.CharField(max_length=50, unique=True, db_index=True)

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    destination = models.CharField(max_length=200, null=True, blank=True)

    tour_date = models.DateTimeField()
    duration_days = models.IntegerField(default=1)

    group_leader_name = models.CharField(max_length=200, null=True, blank=True)
    group_leader_phone = models.CharField(max_length=50, null=True, blank=True)
    number_of_guests = models.IntegerField(default=1)

    price_per_person = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    status = models.CharField(max_length=50, default='confirmed')

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_tours_created',
    )

    class Meta:
        db_table = 'group_tours'

    def __str__(self):
        return f"GroupTour(id={self.id}, tour_number='{self.tour_number}', name='{self.name}')"


class Bill(models.Model):
    """Bill model - Consolidated billing for guests/reservations."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='bills',
        db_index=True,
    )
    bill_number = models.CharField(max_length=50, unique=True, db_index=True)

    guest = models.ForeignKey(
        'Guest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills',
    )
    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills',
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills',
    )

    bill_type = models.CharField(max_length=20, choices=BillType.choices)

    bill_date = models.DateField(db_index=True)
    due_date = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills',
    )
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)

    status = models.CharField(
        max_length=20,
        choices=BillStatus.choices,
        default=BillStatus.PENDING,
    )

    notes = models.TextField(null=True, blank=True)
    internal_notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills_created',
    )

    class Meta:
        db_table = 'bills'

    def __str__(self):
        return f"Bill(id={self.id}, bill_number='{self.bill_number}', total={self.total_amount})"


class BillItem(models.Model):
    """Bill line item."""

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='items',
    )
    billing_item = models.ForeignKey(
        BillingItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill_items',
    )

    description = models.TextField()
    item_type = models.CharField(max_length=50, null=True, blank=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    service_charge_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)

    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)

    charge_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'bill_items'

    def __str__(self):
        desc = self.description[:30] if self.description else ''
        return f"BillItem(id={self.id}, bill_id={self.bill_id}, description='{desc}...')"


class BillPayment(models.Model):
    """Bill payment model."""

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='payments',
    )

    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)

    currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill_payments',
    )
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)
    amount_in_base_currency = models.DecimalField(max_digits=15, decimal_places=2)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill_payments_created',
    )

    class Meta:
        db_table = 'bill_payments'

    def __str__(self):
        return f"BillPayment(id={self.id}, payment_number='{self.payment_number}', amount={self.amount})"

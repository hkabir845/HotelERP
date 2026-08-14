"""Banquet venues, catalogs, events, folio lines, and payments."""
from django.db import models


class BanquetNamed(models.Model):
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


class BanquetVenue(BanquetNamed):
    code = models.CharField(max_length=40, blank=True, default='')
    capacity = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'banquet_venues'


class BanquetVendor(BanquetNamed):
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    service_type = models.CharField(max_length=100, blank=True, default='')
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'banquet_vendors'


class BanquetService(BanquetNamed):
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'banquet_services'


class BanquetItem(BanquetNamed):
    unit = models.CharField(max_length=40, blank=True, default='Pcs')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'banquet_items'


class BanquetPackage(BanquetNamed):
    price_per_pax = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'banquet_packages'


class BanquetSession(BanquetNamed):
    start_time = models.CharField(max_length=8, blank=True, default='')
    end_time = models.CharField(max_length=8, blank=True, default='')

    class Meta:
        db_table = 'banquet_sessions'


class BanquetEvent(models.Model):
    STATUS_CHOICES = [
        ('enquiry', 'Enquiry'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('wedding', 'Wedding'),
        ('conference', 'Conference'),
        ('birthday', 'Birthday'),
        ('corporate', 'Corporate'),
        ('reception', 'Reception'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='banquet_events', db_index=True)
    number = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=40, default='other')
    contact_name = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    company = models.CharField(max_length=200, blank=True, default='')
    venue = models.ForeignKey(
        BanquetVenue, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    session = models.ForeignKey(
        BanquetSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    event_date = models.DateField(db_index=True)
    start_time = models.CharField(max_length=8, blank=True, default='')
    end_time = models.CharField(max_length=8, blank=True, default='')
    pax = models.PositiveIntegerField(default=0)
    package = models.ForeignKey(
        BanquetPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    package_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lines_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='enquiry', db_index=True)
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name='banquet_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'banquet_events'
        ordering = ['-event_date', '-id']
        indexes = [models.Index(fields=['tenant', 'status', 'event_date'])]

    def __str__(self):
        return f"BanquetEvent({self.number})"


class BanquetEventLine(models.Model):
    LINE_TYPES = [
        ('service', 'Service'),
        ('item', 'Item'),
        ('vendor', 'Vendor'),
    ]

    event = models.ForeignKey(BanquetEvent, on_delete=models.CASCADE, related_name='lines')
    line_type = models.CharField(max_length=20)
    service = models.ForeignKey(
        BanquetService, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_lines'
    )
    item = models.ForeignKey(
        BanquetItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_lines'
    )
    vendor = models.ForeignKey(
        BanquetVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_lines'
    )
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'banquet_event_lines'
        ordering = ['id']


class BanquetEventPayment(models.Model):
    event = models.ForeignKey(BanquetEvent, on_delete=models.CASCADE, related_name='payments')
    pay_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, default='cash')
    notes = models.CharField(max_length=255, blank=True, default='')
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name='banquet_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'banquet_event_payments'
        ordering = ['-pay_date', '-id']

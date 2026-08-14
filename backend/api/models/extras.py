"""GYOROOM-style extra service modules: laundry, spa, hall, pool, channel."""
from django.db import models


class ServiceBooking(models.Model):
    KIND_CHOICES = [
        ('laundry', 'Laundry'),
        ('laundry_stock', 'Laundry stock'),
        ('spa', 'Spa'),
        ('hall', 'Hall'),
        ('pool', 'Pool'),
        ('pool_package', 'Pool package'),
        ('travel', 'Travel desk'),
    ]

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='service_bookings', db_index=True)
    kind = models.CharField(max_length=30, db_index=True)
    reference = models.CharField(max_length=50, db_index=True)
    guest_name = models.CharField(max_length=200, blank=True, default='')
    room_number = models.CharField(max_length=50, blank=True, default='')
    item = models.CharField(max_length=200, blank=True, default='')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default='open')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_bookings'
        ordering = ['-created_at']


class ChannelMapping(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='channel_mappings', db_index=True)
    channel_name = models.CharField(max_length=100)
    property_code = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'channel_mappings'
        ordering = ['channel_name']


class CatalogRecord(models.Model):
    """Generic list/create rows for GYOROOM-matched operational screens."""

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='catalog_records', db_index=True)
    kind = models.CharField(max_length=80, db_index=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=80, blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=40, default='active')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'catalog_records'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['tenant', 'kind'])]


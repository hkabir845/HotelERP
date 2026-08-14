"""Room and RoomType models."""
from django.db import models


class RoomStatusEnum(models.TextChoices):
    """Room status."""

    AVAILABLE = 'available', 'Available'
    OCCUPIED = 'occupied', 'Occupied'
    OUT_OF_ORDER = 'out_of_order', 'Out of Order'
    MAINTENANCE = 'maintenance', 'Maintenance'
    CLEANING = 'cleaning', 'Cleaning'
    RESERVED = 'reserved', 'Reserved'


class RoomType(models.Model):
    """Room type model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_types',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    max_occupancy = models.IntegerField(default=2)
    extra_occupancy = models.IntegerField(default=0)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    extra_bed_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amenities = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'room_types'

    def __str__(self):
        return f"RoomType(id={self.id}, name='{self.name}')"


class Room(models.Model):
    """Room model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='rooms',
        db_index=True,
    )
    room_number = models.CharField(max_length=20, db_index=True)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='rooms',
    )
    floor = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RoomStatusEnum.choices,
        default=RoomStatusEnum.AVAILABLE,
    )

    bed_type = models.CharField(max_length=50, null=True, blank=True)
    view = models.CharField(max_length=100, null=True, blank=True)
    smoking_allowed = models.BooleanField(default=False)

    rack_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'rooms'

    def __str__(self):
        return f"Room(id={self.id}, room_number='{self.room_number}', status='{self.status}')"

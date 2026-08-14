"""Reservation model."""
from django.db import models


class ReservationStatus(models.TextChoices):
    """Reservation status."""

    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CHECKED_IN = 'checked_in', 'Checked In'
    CHECKED_OUT = 'checked_out', 'Checked Out'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'


class ReservationType(models.TextChoices):
    """Reservation type."""

    INDIVIDUAL = 'individual', 'Individual'
    GROUP = 'group', 'Group'
    CORPORATE = 'corporate', 'Corporate'
    WALK_IN = 'walk_in', 'Walk In'


class Reservation(models.Model):
    """Reservation model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='reservations',
        db_index=True,
    )
    reservation_number = models.CharField(max_length=50, unique=True, db_index=True)

    guest = models.ForeignKey(
        'Guest',
        on_delete=models.CASCADE,
        related_name='reservations',
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
    )

    check_in_date = models.DateTimeField(db_index=True)
    check_out_date = models.DateTimeField(db_index=True)
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
    )
    reservation_type = models.CharField(
        max_length=20,
        choices=ReservationType.choices,
        default=ReservationType.INDIVIDUAL,
    )

    room_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)

    special_requests = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    source = models.CharField(max_length=100, null=True, blank=True)
    booking_agent = models.CharField(max_length=100, null=True, blank=True)
    board_type = models.CharField(max_length=100, null=True, blank=True)

    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations_created',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'reservations'

    def __str__(self):
        return (
            f"Reservation(id={self.id}, reservation_number='{self.reservation_number}', "
            f"status='{self.status}')"
        )

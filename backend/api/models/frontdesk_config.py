"""Frontdesk configuration models."""
from django.db import models


class GuestSource(models.Model):
    """Guest source model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='guest_sources',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'guest_sources'

    def __str__(self):
        return f"GuestSource(id={self.id}, name='{self.name}')"


class BookingAgent(models.Model):
    """Booking agent model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='booking_agents',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'booking_agents'

    def __str__(self):
        return f"BookingAgent(id={self.id}, name='{self.name}')"


class Company(models.Model):
    """Company model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='companies',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'companies'

    def __str__(self):
        return f"Company(id={self.id}, name='{self.name}')"


class RatePlan(models.Model):
    """Rate plan model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='rate_plans',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'rate_plans'

    def __str__(self):
        return f"RatePlan(id={self.id}, name='{self.name}')"


class CancellationRule(models.Model):
    """Cancellation rule model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='cancellation_rules',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    hours_before_checkin = models.IntegerField(null=True, blank=True)
    cancellation_charge_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    cancellation_charge_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'cancellation_rules'

    def __str__(self):
        return f"CancellationRule(id={self.id}, name='{self.name}')"


class BoardType(models.Model):
    """Board type model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='board_types',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    additional_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'board_types'

    def __str__(self):
        return f"BoardType(id={self.id}, name='{self.name}')"


class ComplimentaryOption(models.Model):
    """Complimentary option model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='complimentary_options',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'complimentary_options'

    def __str__(self):
        return f"ComplimentaryOption(id={self.id}, name='{self.name}')"


class RoomViewType(models.Model):
    """Room view type model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_view_types',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'room_view_types'

    def __str__(self):
        return f"RoomViewType(id={self.id}, name='{self.name}')"


class BedInfo(models.Model):
    """Bed info model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='bed_info',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'bed_info'
        verbose_name_plural = 'bed info'

    def __str__(self):
        return f"BedInfo(id={self.id}, name='{self.name}')"


class RoomFacility(models.Model):
    """Room facility model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_facilities',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'room_facilities'
        verbose_name_plural = 'room facilities'

    def __str__(self):
        return f"RoomFacility(id={self.id}, name='{self.name}')"


class RoomGroup(models.Model):
    """Room group model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_groups',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'room_groups'

    def __str__(self):
        return f"RoomGroup(id={self.id}, name='{self.name}')"


class ExtraChargeGroup(models.Model):
    """Extra charge group model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='extra_charge_groups',
        db_index=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'extra_charge_groups'

    def __str__(self):
        return f"ExtraChargeGroup(id={self.id}, name='{self.name}')"


class ExtraChargeItem(models.Model):
    """Extra charge item model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='extra_charge_items',
        db_index=True,
    )
    group = models.ForeignKey(
        ExtraChargeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'extra_charge_items'

    def __str__(self):
        return f"ExtraChargeItem(id={self.id}, name='{self.name}', amount={self.amount})"


class RoomTypeSpecialRate(models.Model):
    """Date-range special rate for a room type (optional rate plan)."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_type_special_rates',
        db_index=True,
    )
    room_type = models.ForeignKey(
        'RoomType',
        on_delete=models.CASCADE,
        related_name='special_rates',
    )
    rate_plan = models.ForeignKey(
        RatePlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='special_rates',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'room_type_special_rates'

    def __str__(self):
        return (
            f"RoomTypeSpecialRate(id={self.id}, room_type_id={self.room_type_id}, "
            f"rate={self.rate})"
        )


class Package(models.Model):
    """Package model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='packages',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'packages'

    def __str__(self):
        return f"Package(id={self.id}, name='{self.name}', price={self.price})"


class AmenityDistribution(models.Model):
    """Amenity distribution model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='amenity_distributions',
        db_index=True,
    )
    distribution_number = models.CharField(max_length=50, unique=True, db_index=True)

    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='amenity_distributions',
    )

    distribution_date = models.DateTimeField()
    distributed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='amenity_distributions',
    )

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'amenity_distributions'

    def __str__(self):
        return (
            f"AmenityDistribution(id={self.id}, "
            f"distribution_number='{self.distribution_number}')"
        )


class AmenityDistributionItem(models.Model):
    """Amenity distribution item model."""

    distribution = models.ForeignKey(
        AmenityDistribution,
        on_delete=models.CASCADE,
        related_name='items',
    )

    item_name = models.CharField(max_length=200)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'amenity_distribution_items'

    def __str__(self):
        return (
            f"AmenityDistributionItem(id={self.id}, item_name='{self.item_name}', "
            f"quantity={self.quantity})"
        )


class WakeUpCall(models.Model):
    """Wake up call model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='wake_up_calls',
        db_index=True,
    )

    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='wake_up_calls',
    )
    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wake_up_calls',
    )

    call_time = models.DateTimeField(db_index=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wake_up_calls_created',
    )

    class Meta:
        db_table = 'wake_up_calls'

    def __str__(self):
        return f"WakeUpCall(id={self.id}, room_id={self.room_id}, call_time='{self.call_time}')"


class LostFound(models.Model):
    """Lost & Found model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='lost_found_items',
        db_index=True,
    )

    item_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    location_found = models.CharField(max_length=200, null=True, blank=True)
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lost_found_items',
    )

    found_date = models.DateTimeField()
    found_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lost_found_reported',
    )

    status = models.CharField(max_length=50, default='found')
    claimed_by = models.CharField(max_length=200, null=True, blank=True)
    claimed_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'lost_found'

    def __str__(self):
        return f"LostFound(id={self.id}, item_name='{self.item_name}', status='{self.status}')"


class AgentFundRequest(models.Model):
    """Agent fund request model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='agent_fund_requests',
        db_index=True,
    )
    request_number = models.CharField(max_length=50, unique=True, db_index=True)

    agent = models.ForeignKey(
        BookingAgent,
        on_delete=models.CASCADE,
        related_name='fund_requests',
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    request_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')

    notes = models.TextField(null=True, blank=True)

    requested_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_fund_requests_requested',
    )
    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_fund_requests_approved',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'agent_fund_requests'

    def __str__(self):
        return (
            f"AgentFundRequest(id={self.id}, request_number='{self.request_number}', "
            f"amount={self.amount})"
        )

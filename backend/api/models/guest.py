"""Guest model."""
from django.db import models


class Guest(models.Model):
    """Guest model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='guests',
        db_index=True,
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)

    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    id_type = models.CharField(max_length=50, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    id_expiry = models.DateField(null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)

    preferences = models.TextField(null=True, blank=True)
    special_requests = models.TextField(null=True, blank=True)

    loyalty_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    loyalty_points = models.IntegerField(default=0)

    is_vip = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    last_visit = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'guests'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f"Guest(id={self.id}, name='{self.full_name}', email='{self.email}')"

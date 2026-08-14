"""Utilities: blog, property info, roles, extra config, account permissions."""
from django.db import models


class UtilityBlog(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='utility_blogs', db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default='')
    is_published = models.BooleanField(default=False)
    published_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utility_blogs'
        ordering = ['-id']


class PropertyImage(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='property_images', db_index=True)
    caption = models.CharField(max_length=200, blank=True, default='')
    image_url = models.CharField(max_length=500)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_images'
        ordering = ['sort_order', 'id']


class NearbyTerminal(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='nearby_terminals', db_index=True)
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=40, default='airport')
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nearby_terminals'
        ordering = ['name']


class AcceptedPaymentMethod(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='accepted_payment_methods', db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accepted_payment_methods'
        ordering = ['name']


class AppRole(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='app_roles', db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    modules = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_roles'
        ordering = ['name']


class UserAccountPermission(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='user_account_permissions')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='account_permissions')
    can_post_vouchers = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_manage_coa = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_account_permissions'
        unique_together = ('tenant', 'user')


class UtilitySettings(models.Model):
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE, related_name='utility_settings')
    check_in_time = models.CharField(max_length=8, default='14:00')
    check_out_time = models.CharField(max_length=8, default='12:00')
    tax_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    service_charge_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sms_unit_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.5)
    night_audit_time = models.CharField(max_length=8, default='23:59')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'utility_settings'

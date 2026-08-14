"""Operational records for banquet, CRM, leave, loans, and similar workflows."""
from django.db import models


class OpsRecord(models.Model):
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='ops_records', db_index=True)
    kind = models.CharField(max_length=80, db_index=True)
    reference = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=200, blank=True, default='')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=40, default='open', db_index=True)
    notes = models.TextField(blank=True, default='')
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_records'
        ordering = ['-id']
        indexes = [models.Index(fields=['tenant', 'kind', 'status'])]

    def __str__(self):
        return f"OpsRecord({self.kind}, {self.reference})"

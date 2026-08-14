"""Audit trail for frontdesk and folio actions."""
from django.db import models


class AuditLog(models.Model):
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=40, db_index=True)
    entity = models.CharField(max_length=40, db_index=True)
    entity_id = models.IntegerField(null=True, blank=True)
    reference = models.CharField(max_length=80, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"AuditLog(id={self.id}, action='{self.action}', reference='{self.reference}')"

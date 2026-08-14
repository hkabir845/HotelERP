"""Public website CMS records (mirrors the Turag resort site API)."""
from django.db import models


class WebsiteContact(models.Model):
    """Contact form submissions from the public landing page."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='website_contacts',
        db_index=True,
    )
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, default='')
    subject = models.CharField(max_length=255, blank=True, default='')
    message = models.TextField()
    status = models.CharField(max_length=20, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'website_contacts'
        ordering = ['-created_at']

"""Broadcast Message model."""
from django.db import models


class MessageType(models.TextChoices):
    """Message type."""

    INFO = 'info', 'Info'
    WARNING = 'warning', 'Warning'
    ERROR = 'error', 'Error'
    SUCCESS = 'success', 'Success'
    ANNOUNCEMENT = 'announcement', 'Announcement'


class MessagePriority(models.TextChoices):
    """Message priority."""

    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class BroadcastMessage(models.Model):
    """Broadcast message model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='broadcast_messages',
        db_index=True,
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.INFO,
    )
    priority = models.CharField(
        max_length=20,
        choices=MessagePriority.choices,
        default=MessagePriority.MEDIUM,
    )

    send_to_all = models.BooleanField(default=False)
    send_to_tenant = models.BooleanField(default=False)
    send_to_department = models.CharField(max_length=100, null=True, blank=True)
    send_to_users = models.TextField(null=True, blank=True)

    send_immediately = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    channel = models.CharField(max_length=20, default='in_app')
    recipient_count = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broadcast_messages_created',
    )

    class Meta:
        db_table = 'broadcast_messages'

    def __str__(self):
        return f"BroadcastMessage(id={self.id}, title='{self.title}', type='{self.message_type}')"


class MessageRead(models.Model):
    """Message read tracking."""

    message = models.ForeignKey(
        BroadcastMessage,
        on_delete=models.CASCADE,
        related_name='read_by',
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='messages_read',
    )

    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_reads'

    def __str__(self):
        return f"MessageRead(message_id={self.message_id}, user_id={self.user_id})"

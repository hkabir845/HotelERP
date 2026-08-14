"""Housekeeping models."""
from django.db import models


class TaskStatus(models.TextChoices):
    """Task status."""

    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class TaskPriority(models.TextChoices):
    """Task priority."""

    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class TaskType(models.TextChoices):
    """Task type."""

    CLEANING = 'cleaning', 'Cleaning'
    INSPECTION = 'inspection', 'Inspection'
    MAINTENANCE = 'maintenance', 'Maintenance'
    DEEP_CLEAN = 'deep_clean', 'Deep Clean'
    TURNDOWN = 'turndown', 'Turndown'


class RoomStatus(models.Model):
    """Room status tracking."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='room_statuses',
        db_index=True,
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='room_statuses',
        db_index=True,
    )

    status = models.CharField(max_length=50)
    housekeeping_status = models.CharField(max_length=50, null=True, blank=True)

    last_cleaned = models.DateTimeField(null=True, blank=True)
    last_inspected = models.DateTimeField(null=True, blank=True)
    next_cleaning_due = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='room_status_updates',
    )

    class Meta:
        db_table = 'room_status'

    def __str__(self):
        return f"RoomStatus(id={self.id}, room_id={self.room_id}, status='{self.status}')"


class HousekeepingTask(models.Model):
    """Housekeeping task model."""

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='housekeeping_tasks',
        db_index=True,
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='housekeeping_tasks',
        db_index=True,
    )

    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
    )

    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='housekeeping_tasks_assigned',
    )
    assigned_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='housekeeping_tasks_assigned_by',
    )

    scheduled_date = models.DateTimeField(db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    inspection_notes = models.TextField(null=True, blank=True)

    inspected_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='housekeeping_tasks_inspected',
    )
    inspection_date = models.DateTimeField(null=True, blank=True)
    passed_inspection = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'housekeeping_tasks'

    def __str__(self):
        return f"HousekeepingTask(id={self.id}, room_id={self.room_id}, status='{self.status}')"

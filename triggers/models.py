from django.db import models
from django.utils.timezone import now
from datetime import timedelta


class BaseTrigger(models.Model):
    """
    Abstract base class for triggers with shared fields and methods.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Makes this an abstract model

    def __str__(self):
        return self.name


class ScheduledTrigger(BaseTrigger):
    """
    Model for scheduled triggers.
    """
    schedule_time = models.DateTimeField(blank=True, null=True)  # One-time trigger
    is_recurring = models.BooleanField(default=False)  # Indicates recurring or one-time
    interval = models.DurationField(blank=True, null=True)  # Interval for recurring triggers
    end_time = models.DateTimeField(blank=True, null=True)  # End time for recurring triggers

    def validate_trigger(self):
        """
        Validation for scheduled triggers.
        """
        if not self.schedule_time and not self.is_recurring:
            raise ValueError("Schedule time must be set for one-time triggers.")
        if self.is_recurring and not self.interval:
            raise ValueError("Interval must be provided for recurring triggers.")
        if self.is_recurring and self.end_time and self.end_time <= now():
            raise ValueError("End time for recurring trigger must be in the future.")

    def save(self, *args, **kwargs):
        self.validate_trigger()
        super().save(*args, **kwargs)


class APITrigger(BaseTrigger):
    """
    Model for API triggers.
    """
    payload = models.JSONField(blank=True, null=True)  # API-specific payload

    def validate_trigger(self):
        """
        Validation for API triggers.
        """
        if not self.payload:
            raise ValueError("Payload must be provided for API triggers.")

    def save(self, *args, **kwargs):
        self.validate_trigger()
        super().save(*args, **kwargs)


class EventLog(models.Model):
    """
    Model to log events for both Scheduled and API triggers.
    """
    TRIGGER_TYPES = [
        ('SCHEDULED', 'Scheduled Trigger'),
        ('API', 'API Trigger'),
    ]

    trigger_type = models.CharField(max_length=10, choices=TRIGGER_TYPES)
    trigger_id = models.PositiveIntegerField()  # ID of the associated trigger
    fired_at = models.DateTimeField(auto_now_add=True)  # Time when the event fired
    payload = models.JSONField(blank=True, null=True)  # API payload or testing data
    is_test = models.BooleanField(default=False)  # Indicates manual/test trigger
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),  # Event is active and in the 2-hour window
            ('ARCHIVED', 'Archived'),  # Event is older than 2 hours but less than 48 hours
        ],
        default='ACTIVE',
    )

    def __str__(self):
        return f"Event {self.trigger_id} ({self.trigger_type}) at {self.fired_at}"

    def archive_if_needed(self):
        """
        Automatically update the status to 'ARCHIVED' after 2 hours.
        """
        if self.status == 'ACTIVE' and now() >= self.fired_at + timedelta(hours=2):
            self.status = 'ARCHIVED'
            self.save()

    def delete_if_expired(self):
        """
        Delete the event log after 48 hours.
        """
        if now() >= self.fired_at + timedelta(hours=48):
            self.delete()


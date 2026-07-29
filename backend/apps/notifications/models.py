from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel


class Notification(OrganizationScopedModel):
    """An in-app notification for a single user, triggered by a domain
    event elsewhere in the platform (a lease activating, a payment
    clearing, a maintenance request changing status...). Created
    exclusively by `apps.notifications.services`, invoked from
    `apps.notifications.signals` — the apps that raise these events
    (leases, payments, maintenance) have no idea notifications exist.
    """

    class NotificationType(models.TextChoices):
        LEASE_ACTIVATED = "lease_activated", "Lease Activated"
        LEASE_TERMINATED = "lease_terminated", "Lease Terminated"
        PAYMENT_RECEIVED = "payment_received", "Payment Received"
        PAYMENT_REFUNDED = "payment_refunded", "Payment Refunded"
        MAINTENANCE_REPORTED = "maintenance_reported", "Maintenance Reported"
        MAINTENANCE_STATUS_CHANGED = "maintenance_status_changed", "Maintenance Status Changed"
        GENERIC = "generic", "Generic"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=40, choices=NotificationType.choices, default=NotificationType.GENERIC)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True, help_text="Relative frontend path, e.g. /leases")
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [models.Index(fields=["organization", "recipient", "is_read"])]

    def __str__(self):
        return f"{self.title} -> {self.recipient_id}"

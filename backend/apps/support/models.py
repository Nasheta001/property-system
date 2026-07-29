from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel


class SupportTicket(OrganizationScopedModel):
    """A request from an organization to the platform's own support team —
    distinct from `apps.maintenance.MaintenanceRequest`, which is a
    tenant's issue with a physical unit. `created_by` (from `BaseModel`)
    is who raised it; `assigned_to` is the platform staff member handling
    it, set via Django admin rather than this app's API — the org-facing
    API only ever needs to create tickets, watch their status, and close
    them, never triage who's working the queue.
    """

    class Category(models.TextChoices):
        BILLING = "billing", "Billing"
        TECHNICAL = "technical", "Technical"
        FEATURE_REQUEST = "feature_request", "Feature Request"
        BUG_REPORT = "bug_report", "Bug Report"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_ON_CUSTOMER = "waiting_on_customer", "Waiting on Customer"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True, blank=True
    )

    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.subject


class SupportTicketComment(OrganizationScopedModel):
    """A reply on a ticket. `is_internal` notes are staff-only — visible in
    Django admin, filtered out of every response the organization-facing
    API returns (see `apps.support.views`).
    """

    ticket = models.ForeignKey(SupportTicket, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    is_internal = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Support Ticket Comment"
        verbose_name_plural = "Support Ticket Comments"

    def __str__(self):
        return f"Comment on {self.ticket_id}"

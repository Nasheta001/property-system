from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel
from apps.maintenance.validators import validate_attachment_file


class Vendor(OrganizationScopedModel):
    """An external contractor an organization dispatches maintenance work to."""

    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    specialty = models.CharField(max_length=150, blank=True, help_text="e.g. Plumbing, Electrical")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"

    def __str__(self):
        return self.name


class MaintenanceRequest(OrganizationScopedModel):
    """A maintenance issue reported against a unit, tracked through a fixed
    workflow. Every forward transition (verify/assign/accept/start/wait for
    parts/complete/review/close) is enforced by `apps.maintenance.services`,
    never by writing `status` directly — see that module for the allowed
    transitions.
    """

    class Category(models.TextChoices):
        PLUMBING = "plumbing", "Plumbing"
        ELECTRICAL = "electrical", "Electrical"
        APPLIANCE = "appliance", "Appliance"
        STRUCTURAL = "structural", "Structural"
        HVAC = "hvac", "HVAC"
        PEST_CONTROL = "pest_control", "Pest Control"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        VERIFIED = "verified", "Verified"
        ASSIGNED = "assigned", "Assigned"
        ACCEPTED = "accepted", "Accepted"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_PARTS = "waiting_parts", "Waiting Parts"
        COMPLETED = "completed", "Completed"
        REVIEWED = "reviewed", "Reviewed"
        CLOSED = "closed", "Closed"

    unit = models.ForeignKey("properties.Unit", related_name="maintenance_requests", on_delete=models.PROTECT)
    tenant = models.ForeignKey(
        "tenants.TenantProfile",
        related_name="maintenance_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True, blank=True
    )
    vendor = models.ForeignKey(
        Vendor, related_name="maintenance_requests", on_delete=models.SET_NULL, null=True, blank=True
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED, db_index=True)

    assigned_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Maintenance Request"
        verbose_name_plural = "Maintenance Requests"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "priority"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.unit_id})"


class MaintenanceComment(OrganizationScopedModel):
    """A note on a maintenance request's progress — visible to anyone in
    the organization who can see the request itself (property manager,
    the reporting tenant, etc.).
    """

    request = models.ForeignKey(MaintenanceRequest, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True)
    body = models.TextField()

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Maintenance Comment"
        verbose_name_plural = "Maintenance Comments"

    def __str__(self):
        return f"Comment on {self.request_id}"


class MaintenanceAttachment(OrganizationScopedModel):
    """A photo or video evidencing the issue (or the completed repair)."""

    request = models.ForeignKey(MaintenanceRequest, related_name="attachments", on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="maintenance/%Y/%m/", validators=[validate_attachment_file])
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Maintenance Attachment"
        verbose_name_plural = "Maintenance Attachments"

    def __str__(self):
        return self.file.name

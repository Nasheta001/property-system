from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import OrganizationScopedModel


class Lease(OrganizationScopedModel):
    """A tenancy agreement binding one `TenantProfile` to one `Unit` for a
    date range. Status transitions (draft → active → terminated/expired)
    are enforced by `apps.leases.services`, not by direct field writes —
    activating/terminating a lease also flips the unit's occupancy status,
    and those two things must always change together.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PENDING_RENEWAL = "pending_renewal", "Pending Renewal"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"

    unit = models.ForeignKey("properties.Unit", related_name="leases", on_delete=models.PROTECT)
    tenant = models.ForeignKey("tenants.TenantProfile", related_name="leases", on_delete=models.PROTECT)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for a month-to-month lease.")

    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    billing_day = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Day of the month rent is due.",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    terminated_at = models.DateTimeField(null=True, blank=True)
    termination_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Lease"
        verbose_name_plural = "Leases"
        indexes = [models.Index(fields=["organization", "status"])]
        constraints = [
            models.UniqueConstraint(
                fields=["unit"],
                condition=models.Q(status="active"),
                name="unique_active_lease_per_unit",
            ),
        ]

    def __str__(self):
        return f"{self.tenant} @ {self.unit} ({self.status})"

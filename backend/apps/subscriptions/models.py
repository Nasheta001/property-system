from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel
from apps.organizations.models import Organization


class SubscriptionEvent(OrganizationScopedModel):
    """An append-only record of every plan change an organization makes —
    the audit trail a billing dispute or support ticket needs. Like
    `LedgerEntry`/`ActivityLog`, it is written once by
    `apps.subscriptions.services.change_plan` and never edited.
    """

    previous_plan = models.CharField(max_length=20, choices=Organization.SubscriptionPlan.choices)
    new_plan = models.CharField(max_length=20, choices=Organization.SubscriptionPlan.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Subscription Event"
        verbose_name_plural = "Subscription Events"
        indexes = [models.Index(fields=["organization", "created_at"])]

    def __str__(self):
        return f"{self.organization_id}: {self.previous_plan} -> {self.new_plan}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Subscription events are immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Subscription events are a permanent billing record and cannot be deleted.")

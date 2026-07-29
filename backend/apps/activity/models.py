from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel


class ActivityLog(OrganizationScopedModel):
    """An append-only record of a notable event in the organization —
    powers both the dashboard's activity feed and, since it's immutable,
    doubles as a lightweight audit trail of who did what and when.

    Written exclusively by `apps.activity.services.log_activity`, called
    from `apps.activity.signals` — same decoupled shape as
    `apps.notifications`: the apps that raise these events have no idea
    this one is listening.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True, blank=True
    )
    actor_name = models.CharField(max_length=255, blank=True, help_text="Snapshot in case the actor is later removed.")
    verb = models.CharField(max_length=255)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    target_link = models.CharField(max_length=255, blank=True, help_text="Relative frontend path, e.g. /leases")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Activity Log Entry"
        verbose_name_plural = "Activity Log Entries"
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["organization", "target_type"]),
        ]

    def __str__(self):
        return f"{self.actor_name or 'System'} {self.verb}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Activity log entries are immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Activity log entries are a permanent record and cannot be deleted.")

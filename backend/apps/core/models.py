import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    """Default manager that hides soft-deleted rows.

    Use `all_objects` on a model to reach soft-deleted rows when needed
    (e.g. admin views, restore flows, audit reports).
    """

    def __init__(self, *args, alive_only=True, **kwargs):
        self.alive_only = alive_only
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = SoftDeleteQuerySet(self.model, using=self._db)
        return qs.alive() if self.alive_only else qs


class SoftDeleteModel(models.Model):
    """Soft delete support: rows are flagged, never destroyed, by default."""

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["deleted_at"])
        return (1, {self._meta.label: 1})

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class UUIDModel(models.Model):
    """Primary key as UUID4 — safe to expose in URLs, non-enumerable."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AuditModel(models.Model):
    """Tracks which user created / last updated a row."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel, SoftDeleteModel, AuditModel):
    """Standard base for every domain model in the platform."""

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class OrganizationScopedModel(BaseModel):
    """Base for any model that belongs to exactly one tenant (Organization).

    Combined with `apps.core.permissions.IsOrganizationMember` and the
    `TenantScopedViewSetMixin`, this guarantees rows are always filtered by
    the caller's active organization before they reach a view.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="%(class)ss",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

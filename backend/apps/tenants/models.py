from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel


class TenantProfile(OrganizationScopedModel):
    """A person renting (or who has rented) a unit.

    Deliberately distinct from the platform `User` account: most tenants
    are recorded here by a property manager long before — or without ever
    — receiving portal login access. `user` links the two once that access
    is granted.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tenant_profiles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32)
    national_id = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    employer = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=32, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [models.Index(fields=["organization", "last_name", "first_name"])]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

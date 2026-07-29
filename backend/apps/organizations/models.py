from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class Organization(BaseModel):
    """The tenant root. Every piece of domain data in the platform
    (properties, leases, payments, maintenance...) ultimately belongs to
    exactly one Organization, and no query may ever cross that boundary.
    """

    class SubscriptionPlan(models.TextChoices):
        TRIAL = "trial", "Trial"
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_organizations",
        on_delete=models.SET_NULL,
        null=True,
    )

    subscription_plan = models.CharField(
        max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.TRIAL
    )
    is_active = models.BooleanField(default=True)

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=8, default="USD")

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug


class Membership(BaseModel):
    """Links a User to an Organization with a single role. A user may hold
    a different Membership (and therefore a different role) in as many
    organizations as they belong to.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        PROPERTY_MANAGER = "property_manager", "Property Manager"
        LANDLORD = "landlord", "Landlord"
        ACCOUNTANT = "accountant", "Accountant"
        AUDITOR = "auditor", "Auditor"
        VENDOR = "vendor", "Maintenance Vendor"
        TENANT = "tenant", "Tenant"

    organization = models.ForeignKey(Organization, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memberships", on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "user"], name="unique_membership_per_org"),
        ]
        ordering = ["-created_at"]
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    def __str__(self):
        return f"{self.user_id} @ {self.organization_id} ({self.role})"

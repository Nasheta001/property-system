from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import OrganizationScopedModel


class Property(OrganizationScopedModel):
    """A managed property (e.g. "Green Apartments, Bamburi"). Sits directly
    under an Organization and owns one or more Buildings.
    """

    class PropertyType(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        MIXED_USE = "mixed_use", "Mixed Use"

    name = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.RESIDENTIAL)
    description = models.TextField(blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        indexes = [models.Index(fields=["organization", "name"])]

    def __str__(self):
        return self.name


class Building(OrganizationScopedModel):
    """A physical block/wing within a Property (e.g. "Block A")."""

    property = models.ForeignKey(Property, related_name="buildings", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Building"
        verbose_name_plural = "Buildings"
        constraints = [
            models.UniqueConstraint(fields=["property", "name"], name="unique_building_name_per_property"),
        ]

    def __str__(self):
        return f"{self.property.name} - {self.name}"


class Floor(OrganizationScopedModel):
    """A floor within a Building. `number` allows negative values for
    basement levels (-1, -2, ...) and 0 for ground floor.
    """

    building = models.ForeignKey(Building, related_name="floors", on_delete=models.CASCADE)
    number = models.IntegerField()
    name = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["number"]
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        constraints = [
            models.UniqueConstraint(fields=["building", "number"], name="unique_floor_number_per_building"),
        ]

    def __str__(self):
        return self.name or f"Floor {self.number}"


class Unit(OrganizationScopedModel):
    """A leasable apartment/office/shop unit — the leaf of the property
    hierarchy and the object leases, tenants and payments attach to.
    """

    class UnitType(models.TextChoices):
        STUDIO = "studio", "Studio"
        ONE_BEDROOM = "one_bedroom", "1 Bedroom"
        TWO_BEDROOM = "two_bedroom", "2 Bedroom"
        THREE_BEDROOM = "three_bedroom", "3 Bedroom"
        PENTHOUSE = "penthouse", "Penthouse"
        OFFICE = "office", "Office"
        SHOP = "shop", "Shop"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        VACANT = "vacant", "Vacant"
        OCCUPIED = "occupied", "Occupied"
        UNDER_MAINTENANCE = "under_maintenance", "Under Maintenance"
        RESERVED = "reserved", "Reserved"

    floor = models.ForeignKey(Floor, related_name="units", on_delete=models.CASCADE)
    unit_number = models.CharField(max_length=32)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.ONE_BEDROOM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VACANT, db_index=True)

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["unit_number"]
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        constraints = [
            models.UniqueConstraint(fields=["floor", "unit_number"], name="unique_unit_number_per_floor"),
        ]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.floor.building.name} / {self.unit_number}"

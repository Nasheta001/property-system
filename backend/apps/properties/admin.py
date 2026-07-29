from django.contrib import admin

from apps.properties.models import Building, Floor, Property, Unit


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 0
    fields = ["name", "code"]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "property_type", "city", "is_active", "created_at"]
    list_filter = ["property_type", "is_active"]
    search_fields = ["name", "city", "address"]
    autocomplete_fields = ["organization"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [BuildingInline]


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 0
    fields = ["number", "name"]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name", "property", "code", "created_at"]
    search_fields = ["name", "code", "property__name"]
    autocomplete_fields = ["property", "organization"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [FloorInline]


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ["unit_number", "unit_type", "status", "rent_amount"]


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ["__str__", "building", "number", "created_at"]
    search_fields = ["name", "building__name"]
    autocomplete_fields = ["building", "organization"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [UnitInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["unit_number", "floor", "unit_type", "status", "rent_amount", "created_at"]
    list_filter = ["status", "unit_type"]
    search_fields = ["unit_number"]
    autocomplete_fields = ["floor", "organization"]
    readonly_fields = ["id", "created_at", "updated_at"]

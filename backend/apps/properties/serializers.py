from rest_framework import serializers

from apps.properties.models import Building, Floor, Property, Unit


class PropertySerializer(serializers.ModelSerializer):
    building_count = serializers.IntegerField(source="buildings.count", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "property_type",
            "description",
            "address",
            "city",
            "country",
            "latitude",
            "longitude",
            "is_active",
            "building_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class _OrganizationScopedParentMixin:
    """Ensures the parent object referenced by a nested write (e.g. a
    Building's `property`) actually belongs to the caller's current
    organization — otherwise a malicious tenant could attach their rows to
    another tenant's hierarchy simply by guessing an id.
    """

    parent_field = None
    parent_queryset = None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        parent = attrs.get(self.parent_field)
        request = self.context.get("request")
        if parent is not None and request is not None and parent.organization_id != request.organization.id:
            raise serializers.ValidationError({self.parent_field: "Does not belong to your organization."})
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            fields[self.parent_field].queryset = self.parent_queryset.filter(organization=request.organization)
        return fields


class BuildingSerializer(_OrganizationScopedParentMixin, serializers.ModelSerializer):
    parent_field = "property"
    parent_queryset = Property.objects.all()
    floor_count = serializers.IntegerField(source="floors.count", read_only=True)

    class Meta:
        model = Building
        fields = ["id", "property", "name", "code", "floor_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class FloorSerializer(_OrganizationScopedParentMixin, serializers.ModelSerializer):
    parent_field = "building"
    parent_queryset = Building.objects.all()
    unit_count = serializers.IntegerField(source="units.count", read_only=True)

    class Meta:
        model = Floor
        fields = ["id", "building", "number", "name", "unit_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UnitSerializer(_OrganizationScopedParentMixin, serializers.ModelSerializer):
    parent_field = "floor"
    parent_queryset = Floor.objects.all()

    class Meta:
        model = Unit
        fields = [
            "id",
            "floor",
            "unit_number",
            "unit_type",
            "status",
            "bedrooms",
            "bathrooms",
            "size_sqm",
            "rent_amount",
            "deposit_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

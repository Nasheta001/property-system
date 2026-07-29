from apps.core.viewsets import TenantScopedModelViewSet
from apps.properties.filters import UnitFilter
from apps.properties.models import Building, Floor, Property, Unit
from apps.properties.serializers import (
    BuildingSerializer,
    FloorSerializer,
    PropertySerializer,
    UnitSerializer,
)


class PropertyViewSet(TenantScopedModelViewSet):
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
    filterset_fields = ["property_type", "is_active", "city"]
    search_fields = ["name", "address", "city"]
    ordering_fields = ["name", "created_at"]


class BuildingViewSet(TenantScopedModelViewSet):
    serializer_class = BuildingSerializer
    queryset = Building.objects.select_related("property")
    filterset_fields = ["property"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]


class FloorViewSet(TenantScopedModelViewSet):
    serializer_class = FloorSerializer
    queryset = Floor.objects.select_related("building")
    filterset_fields = ["building"]
    ordering_fields = ["number", "created_at"]


class UnitViewSet(TenantScopedModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.select_related("floor", "floor__building", "floor__building__property")
    filterset_class = UnitFilter
    search_fields = ["unit_number"]
    ordering_fields = ["unit_number", "rent_amount", "created_at"]

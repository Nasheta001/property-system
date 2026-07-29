import django_filters

from apps.properties.models import Unit


class UnitFilter(django_filters.FilterSet):
    min_rent = django_filters.NumberFilter(field_name="rent_amount", lookup_expr="gte")
    max_rent = django_filters.NumberFilter(field_name="rent_amount", lookup_expr="lte")
    min_bedrooms = django_filters.NumberFilter(field_name="bedrooms", lookup_expr="gte")
    property = django_filters.UUIDFilter(field_name="floor__building__property_id")
    building = django_filters.UUIDFilter(field_name="floor__building_id")

    class Meta:
        model = Unit
        fields = ["status", "unit_type", "floor", "min_rent", "max_rent", "min_bedrooms", "property", "building"]

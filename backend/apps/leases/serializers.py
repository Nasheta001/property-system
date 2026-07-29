from rest_framework import serializers

from apps.leases.models import Lease
from apps.properties.models import Unit
from apps.tenants.models import TenantProfile


class LeaseSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)

    class Meta:
        model = Lease
        fields = [
            "id",
            "unit",
            "unit_number",
            "tenant",
            "tenant_name",
            "start_date",
            "end_date",
            "rent_amount",
            "deposit_amount",
            "billing_day",
            "status",
            "signed_at",
            "terminated_at",
            "termination_reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "signed_at",
            "terminated_at",
            "termination_reason",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            fields["unit"].queryset = Unit.objects.filter(organization=request.organization)
            fields["tenant"].queryset = TenantProfile.objects.filter(organization=request.organization)
        return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")

        unit = attrs.get("unit") or getattr(self.instance, "unit", None)
        tenant = attrs.get("tenant") or getattr(self.instance, "tenant", None)

        if request is not None and getattr(request, "organization", None) is not None:
            if unit is not None and unit.organization_id != request.organization.id:
                raise serializers.ValidationError({"unit": "Does not belong to your organization."})
            if tenant is not None and tenant.organization_id != request.organization.id:
                raise serializers.ValidationError({"tenant": "Does not belong to your organization."})

        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date is not None and end_date is not None and end_date <= start_date:
            raise serializers.ValidationError({"end_date": "End date must be after the start date."})

        return attrs


class LeaseTerminateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")
    terminated_at = serializers.DateTimeField(required=False)

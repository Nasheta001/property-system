from rest_framework import serializers

from apps.leases.models import Lease
from apps.payments.models import LedgerEntry, Payment


class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)
    unit_number = serializers.CharField(source="lease.unit.unit_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "lease",
            "tenant_name",
            "unit_number",
            "amount",
            "method",
            "status",
            "provider_reference",
            "payment_date",
            "receipt_number",
            "receipt_sent_at",
            "failure_reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "provider_reference",
            "receipt_number",
            "receipt_sent_at",
            "failure_reason",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            fields["lease"].queryset = Lease.objects.filter(organization=request.organization)
        return fields

    def validate_lease(self, value):
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            if value.organization_id != request.organization.id:
                raise serializers.ValidationError("Does not belong to your organization.")
        return value


class PaymentTransitionSerializer(serializers.Serializer):
    provider_reference = serializers.CharField(required=False, allow_blank=True, default="")
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class LedgerEntrySerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source="lease.unit.unit_number", read_only=True)
    tenant_name = serializers.CharField(source="lease.tenant.full_name", read_only=True)

    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "lease",
            "unit_number",
            "tenant_name",
            "payment",
            "entry_type",
            "amount",
            "description",
            "created_at",
        ]

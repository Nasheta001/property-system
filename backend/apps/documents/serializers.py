from rest_framework import serializers

from apps.documents.models import Document
from apps.leases.models import Lease
from apps.properties.models import Property
from apps.tenants.models import TenantProfile


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default="")
    property_name = serializers.CharField(source="property.name", read_only=True, default="")
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True, default="")
    unit_number = serializers.CharField(source="lease.unit.unit_number", read_only=True, default="")

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "document_type",
            "file",
            "property",
            "property_name",
            "lease",
            "unit_number",
            "tenant",
            "tenant_name",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uploaded_by_name", "property_name", "tenant_name", "unit_number", "created_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            fields["property"].queryset = Property.objects.filter(organization=request.organization)
            fields["lease"].queryset = Lease.objects.filter(organization=request.organization)
            fields["tenant"].queryset = TenantProfile.objects.filter(organization=request.organization)
        return fields

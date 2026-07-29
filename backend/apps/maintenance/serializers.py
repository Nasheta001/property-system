from rest_framework import serializers

from apps.maintenance.models import MaintenanceAttachment, MaintenanceComment, MaintenanceRequest, Vendor
from apps.properties.models import Unit
from apps.tenants.models import TenantProfile


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "contact_person",
            "phone_number",
            "email",
            "specialty",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaintenanceCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True, default="")

    class Meta:
        model = MaintenanceComment
        fields = ["id", "request", "author_name", "body", "created_at"]
        read_only_fields = ["id", "request", "author_name", "created_at"]


class MaintenanceAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default="")

    class Meta:
        model = MaintenanceAttachment
        fields = ["id", "request", "file", "caption", "uploaded_by_name", "created_at"]
        read_only_fields = ["id", "request", "uploaded_by_name", "created_at"]


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True, default="")
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True, default="")
    vendor_name = serializers.CharField(source="vendor.name", read_only=True, default="")
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)
    attachment_count = serializers.IntegerField(source="attachments.count", read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            "id",
            "unit",
            "unit_number",
            "tenant",
            "tenant_name",
            "reported_by_name",
            "vendor_name",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "assigned_at",
            "accepted_at",
            "completed_at",
            "reviewed_at",
            "closed_at",
            "closure_notes",
            "comment_count",
            "attachment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "reported_by_name",
            "vendor_name",
            "assigned_at",
            "accepted_at",
            "completed_at",
            "reviewed_at",
            "closed_at",
            "closure_notes",
            "comment_count",
            "attachment_count",
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


class AssignVendorSerializer(serializers.Serializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and getattr(request, "organization", None) is not None:
            self.fields["vendor"].queryset = Vendor.objects.filter(organization=request.organization)


class CloseRequestSerializer(serializers.Serializer):
    closure_notes = serializers.CharField(required=False, allow_blank=True, default="")

from rest_framework import serializers

from apps.tenants.models import TenantProfile


class TenantProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    active_lease_id = serializers.SerializerMethodField()

    class Meta:
        model = TenantProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "national_id",
            "date_of_birth",
            "employer",
            "occupation",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
            "active_lease_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_active_lease_id(self, obj):
        # `active_leases` is populated by a Prefetch in TenantProfileViewSet's
        # queryset to avoid one extra query per row.
        active_leases = getattr(obj, "active_leases", None)
        if active_leases is None:
            active_lease = obj.leases.filter(status="active").first()
            return str(active_lease.id) if active_lease else None
        return str(active_leases[0].id) if active_leases else None

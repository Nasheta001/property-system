from rest_framework import serializers

from apps.organizations.models import Organization


class PlatformOrganizationSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source="owner.email", default="", read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    property_count = serializers.IntegerField(read_only=True)
    unit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "subscription_plan",
            "is_active",
            "owner_email",
            "member_count",
            "property_count",
            "unit_count",
            "created_at",
        ]
        read_only_fields = fields


class SuspendOrganizationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class PlanBreakdownSerializer(serializers.Serializer):
    plan = serializers.CharField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class PlatformStatsSerializer(serializers.Serializer):
    total_organizations = serializers.IntegerField()
    active_organizations = serializers.IntegerField()
    suspended_organizations = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    plan_breakdown = PlanBreakdownSerializer(many=True)
    estimated_mrr = serializers.FloatField()

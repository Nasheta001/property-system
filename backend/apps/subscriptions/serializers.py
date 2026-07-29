from rest_framework import serializers

from apps.subscriptions.models import SubscriptionEvent


class PlanSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    price_monthly = serializers.CharField(allow_null=True)
    currency = serializers.CharField()
    limits = serializers.DictField()
    features = serializers.ListField(child=serializers.CharField())


class UsageSerializer(serializers.Serializer):
    properties = serializers.IntegerField()
    units = serializers.IntegerField()
    team_members = serializers.IntegerField()


class CurrentSubscriptionSerializer(serializers.Serializer):
    plan = PlanSerializer()
    usage = UsageSerializer()


class ChangePlanSerializer(serializers.Serializer):
    plan = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class SubscriptionEventSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", default="", read_only=True)

    class Meta:
        model = SubscriptionEvent
        fields = ["id", "previous_plan", "new_plan", "changed_by_name", "reason", "created_at"]
        read_only_fields = fields

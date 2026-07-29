from rest_framework import serializers

from apps.activity.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ["id", "actor_name", "verb", "target_type", "target_id", "target_link", "created_at"]
        read_only_fields = fields

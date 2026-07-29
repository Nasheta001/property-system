from rest_framework import serializers

from apps.support.models import SupportTicket, SupportTicketComment


class SupportTicketCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True, default="")

    class Meta:
        model = SupportTicketComment
        fields = ["id", "ticket", "author_name", "body", "created_at"]
        read_only_fields = ["id", "ticket", "author_name", "created_at"]


class SupportTicketSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default="")
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "subject",
            "description",
            "category",
            "priority",
            "status",
            "created_by_name",
            "assigned_to_name",
            "resolved_at",
            "closed_at",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by_name",
            "assigned_to_name",
            "resolved_at",
            "closed_at",
            "comment_count",
            "created_at",
            "updated_at",
        ]

    def get_comment_count(self, obj):
        return obj.comments.filter(is_internal=False).count()

from apps.activity.models import ActivityLog
from apps.activity.serializers import ActivityLogSerializer
from apps.core.viewsets import TenantScopedReadOnlyModelViewSet


class ActivityLogViewSet(TenantScopedReadOnlyModelViewSet):
    """The organization's shared activity feed — unlike notifications,
    every member sees the same feed (scoped only to their active
    organization), not just events addressed to them.
    """

    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.select_related("actor")
    filterset_fields = ["target_type"]
    ordering_fields = ["created_at"]

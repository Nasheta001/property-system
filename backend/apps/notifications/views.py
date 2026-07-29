from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedReadOnlyModelViewSet
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(TenantScopedReadOnlyModelViewSet):
    """A user only ever sees (and can only ever mark read) their own
    notifications — the organization scoping from `TenantScopedReadOnlyModelViewSet`
    narrows to the active org, and `get_queryset` narrows further to the
    caller, regardless of their role.
    """

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    filterset_fields = ["is_read", "notification_type"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({"detail": "All notifications marked as read."})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return Response({"count": self.get_queryset().filter(is_read=False).count()})

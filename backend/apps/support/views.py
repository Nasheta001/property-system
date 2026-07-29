from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.core.permissions import ROLE_HIERARCHY
from apps.core.viewsets import TenantScopedModelViewSet
from apps.support.models import SupportTicket
from apps.support.serializers import SupportTicketCommentSerializer, SupportTicketSerializer
from apps.support.services import SupportTicketTransitionError, close_ticket, reopen_ticket


class SupportTicketViewSet(TenantScopedModelViewSet):
    """Any organization member can raise, read, and comment on their own
    organization's tickets — support is a universal concern, not a
    landlord-and-up one. Only the ticket's creator or an org admin can
    close/reopen it; the platform's support team triages status and
    assignment separately, through Django admin.
    """

    serializer_class = SupportTicketSerializer
    queryset = SupportTicket.objects.select_related("created_by", "assigned_to")
    filterset_fields = ["status", "category", "priority"]
    search_fields = ["subject", "description"]
    ordering_fields = ["created_at", "priority", "status"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def _assert_can_manage(self, ticket):
        if ticket.created_by_id == self.request.user.id:
            return
        membership = getattr(self.request, "membership", None)
        if membership is not None and ROLE_HIERARCHY.get(membership.role, 0) >= ROLE_HIERARCHY.get("landlord", 0):
            return
        raise PermissionDenied("Only the ticket's creator or an organization admin can do that.")

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        self._assert_can_manage(ticket)
        try:
            ticket = close_ticket(ticket, request.user)
        except SupportTicketTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        self._assert_can_manage(ticket)
        try:
            ticket = reopen_ticket(ticket, request.user)
        except SupportTicketTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        ticket = self.get_object()

        if request.method == "POST":
            serializer = SupportTicketCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                organization=self.request.organization,
                ticket=ticket,
                author=request.user,
                is_internal=False,
                created_by=request.user,
                updated_by=request.user,
            )
            return Response(serializer.data, status=201)

        comments = ticket.comments.filter(is_internal=False).select_related("author")
        return Response(SupportTicketCommentSerializer(comments, many=True).data)

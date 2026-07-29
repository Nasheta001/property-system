from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet
from apps.leases.models import Lease
from apps.leases.serializers import LeaseSerializer, LeaseTerminateSerializer
from apps.leases.services import LeaseTransitionError, activate_lease, terminate_lease


class LeaseViewSet(TenantScopedModelViewSet):
    serializer_class = LeaseSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "landlord"
    queryset = Lease.objects.select_related(
        "unit", "unit__floor", "unit__floor__building", "tenant"
    )
    filterset_fields = ["status", "unit", "tenant"]
    search_fields = ["unit__unit_number", "tenant__first_name", "tenant__last_name", "tenant__email"]
    ordering_fields = ["start_date", "end_date", "created_at", "rent_amount"]

    def perform_destroy(self, instance):
        if instance.status == Lease.Status.ACTIVE:
            raise DRFValidationError({"detail": "Terminate an active lease before deleting it."})
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        lease = self.get_object()
        try:
            lease = activate_lease(lease, request.user)
        except LeaseTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(lease).data)

    @action(detail=True, methods=["post"])
    def terminate(self, request, pk=None):
        lease = self.get_object()
        serializer = LeaseTerminateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            lease = terminate_lease(
                lease,
                request.user,
                reason=serializer.validated_data.get("reason", ""),
                terminated_at=serializer.validated_data.get("terminated_at"),
            )
        except LeaseTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(lease).data)

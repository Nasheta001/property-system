from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.platform_admin.permissions import IsPlatformStaff
from apps.platform_admin.serializers import (
    PlatformOrganizationSerializer,
    PlatformStatsSerializer,
    SuspendOrganizationSerializer,
)
from apps.platform_admin.services import (
    OrganizationStatusError,
    annotated_organizations,
    platform_stats,
    reactivate_organization,
    suspend_organization,
)


class PlatformStatsView(APIView):
    """Cross-organization counts for the platform owner's dashboard."""

    permission_classes = [IsPlatformStaff]

    def get(self, request):
        return Response(PlatformStatsSerializer(platform_stats()).data)


class PlatformOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Every organization on the platform, visible only to staff — this is
    deliberately not `TenantScopedModelViewSet`: there is no tenant to
    scope by, the whole point is seeing across all of them.
    """

    serializer_class = PlatformOrganizationSerializer
    permission_classes = [IsPlatformStaff]
    queryset = annotated_organizations()
    filterset_fields = ["subscription_plan", "is_active"]
    search_fields = ["name", "slug", "owner__email"]
    ordering_fields = ["name", "created_at"]

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        organization = self.get_object()
        serializer = SuspendOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            suspend_organization(organization, request.user, reason=serializer.validated_data.get("reason", ""))
        except OrganizationStatusError as exc:
            raise DRFValidationError({"detail": str(exc)})

        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"])
    def reactivate(self, request, pk=None):
        organization = self.get_object()

        try:
            reactivate_organization(organization, request.user)
        except OrganizationStatusError as exc:
            raise DRFValidationError({"detail": str(exc)})

        return Response(self.get_serializer(self.get_object()).data)

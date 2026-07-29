from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import HasOrganizationRole, IsOrganizationMember
from apps.core.viewsets import TenantScopedReadOnlyModelViewSet
from apps.subscriptions.catalog import PLAN_CATALOG, plan_list
from apps.subscriptions.models import SubscriptionEvent
from apps.subscriptions.serializers import (
    ChangePlanSerializer,
    CurrentSubscriptionSerializer,
    PlanSerializer,
    SubscriptionEventSerializer,
)
from apps.subscriptions.services import SubscriptionPlanError, change_plan, compute_usage


class PlanListView(APIView):
    """The plan catalog is platform-wide, not organization data, but still
    requires an authenticated org member — an unauthenticated visitor sees
    pricing on the marketing site, not this API.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        return Response(PlanSerializer(plan_list(), many=True).data)


class CurrentSubscriptionView(APIView):
    """GET returns the organization's current plan plus live usage against
    its limits, open to any organization member. POST switches plans — the
    `HasOrganizationRole` permission below leaves GET open to all members
    but restricts POST (a write) to admin+, and `change_plan` validates the
    switch against the new plan's limits.
    """

    permission_classes = [HasOrganizationRole]
    required_role = "admin"

    def get(self, request):
        organization = request.organization
        data = {
            "plan": PLAN_CATALOG[organization.subscription_plan],
            "usage": compute_usage(organization),
        }
        return Response(CurrentSubscriptionSerializer(data).data)

    def post(self, request):
        serializer = ChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            change_plan(
                request.organization,
                serializer.validated_data["plan"],
                request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except SubscriptionPlanError as exc:
            raise DRFValidationError({"detail": str(exc)})

        organization = request.organization
        data = {
            "plan": PLAN_CATALOG[organization.subscription_plan],
            "usage": compute_usage(organization),
        }
        return Response(CurrentSubscriptionSerializer(data).data)


class SubscriptionEventViewSet(TenantScopedReadOnlyModelViewSet):
    """Read-only history of plan changes for the current organization."""

    serializer_class = SubscriptionEventSerializer
    queryset = SubscriptionEvent.objects.select_related("changed_by")

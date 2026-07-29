from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet
from apps.organizations.models import Membership, Organization
from apps.organizations.serializers import MembershipSerializer, OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """Organizations are the tenant root, so this viewset does not use
    `TenantScopedModelViewSet` — there is no parent organization to scope
    by yet. Instead, visibility is limited to organizations the caller has
    an active membership in.
    """

    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user, memberships__is_active=True, is_active=True
        ).distinct()

    def perform_update(self, serializer):
        membership = Membership.objects.filter(
            organization=self.get_object(), user=self.request.user, is_active=True, role__in=["owner", "admin"]
        ).first()
        if membership is None:
            raise PermissionDenied("Only an owner or admin can update this organization.")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner_id != self.request.user.id:
            raise PermissionDenied("Only the organization owner can delete this organization.")
        instance.delete(hard=False)


class MembershipViewSet(TenantScopedModelViewSet):
    """Manages who belongs to the current organization (`request.organization`,
    resolved by `CurrentOrganizationMiddleware` from the `X-Organization-ID`
    header). Only owners/admins may invite, change roles, or remove members.
    """

    serializer_class = MembershipSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "admin"
    queryset = Membership.objects.select_related("user", "organization")
    filterset_fields = ["role", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            invited_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

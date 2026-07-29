from rest_framework import viewsets

from apps.core.permissions import IsOrganizationMember


class TenantScopedModelViewSet(viewsets.ModelViewSet):
    """Base viewset for any endpoint backed by an `OrganizationScopedModel`.

    Guarantees, in one place:
      * the caller has an active membership in `request.organization`
        (via `IsOrganizationMember`);
      * every queryset is filtered down to that organization, so a tenant
        can never read or write another tenant's rows regardless of what
        id is requested in the URL;
      * `organization`, `created_by` and `updated_by` are stamped
        automatically on write.
    """

    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, "swagger_fake_view", False) or self.request.organization is None:
            return queryset.none()
        return queryset.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.delete(hard=False)


class TenantScopedReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only counterpart to `TenantScopedModelViewSet`, for endpoints
    backed by rows that are never written through the API — e.g. an
    append-only ledger populated exclusively by domain services.
    """

    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, "swagger_fake_view", False) or self.request.organization is None:
            return queryset.none()
        return queryset.filter(organization=self.request.organization)

from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet
from apps.leases.models import Lease
from apps.tenants.models import TenantProfile
from apps.tenants.serializers import TenantProfileSerializer


class TenantProfileViewSet(TenantScopedModelViewSet):
    serializer_class = TenantProfileSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "landlord"
    queryset = TenantProfile.objects.prefetch_related(
        Prefetch("leases", queryset=Lease.objects.filter(status=Lease.Status.ACTIVE), to_attr="active_leases")
    )
    search_fields = ["first_name", "last_name", "email", "phone_number", "national_id"]
    ordering_fields = ["first_name", "last_name", "created_at"]

    def perform_destroy(self, instance):
        has_active_lease = instance.leases.filter(status=Lease.Status.ACTIVE).exists()
        if has_active_lease:
            raise DRFValidationError({"detail": "This tenant has an active lease and cannot be deleted."})
        super().perform_destroy(instance)

from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet
from apps.maintenance import services as maintenance_services
from apps.maintenance.models import MaintenanceRequest, Vendor
from apps.maintenance.permissions import MaintenanceRequestPermission
from apps.maintenance.serializers import (
    AssignVendorSerializer,
    CloseRequestSerializer,
    MaintenanceAttachmentSerializer,
    MaintenanceCommentSerializer,
    MaintenanceRequestSerializer,
    VendorSerializer,
)
from apps.maintenance.services import MaintenanceTransitionError


class VendorViewSet(TenantScopedModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "landlord"
    queryset = Vendor.objects.all()
    filterset_fields = ["is_active", "specialty"]
    search_fields = ["name", "contact_person", "specialty"]
    ordering_fields = ["name", "created_at"]


class MaintenanceRequestViewSet(TenantScopedModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [MaintenanceRequestPermission]
    queryset = MaintenanceRequest.objects.select_related("unit", "tenant", "vendor", "reported_by")
    filterset_fields = ["status", "priority", "category", "unit", "vendor"]
    search_fields = ["title", "description", "unit__unit_number"]
    ordering_fields = ["created_at", "priority", "status"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            reported_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def _apply_transition(self, transition_fn, **kwargs):
        instance = self.get_object()
        try:
            instance = transition_fn(instance, self.request.user, **kwargs)
        except MaintenanceTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        return self._apply_transition(maintenance_services.verify)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        serializer = AssignVendorSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        return self._apply_transition(maintenance_services.assign, vendor=serializer.validated_data["vendor"])

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        return self._apply_transition(maintenance_services.accept)

    @action(detail=True, methods=["post"], url_path="start-progress")
    def start_progress(self, request, pk=None):
        return self._apply_transition(maintenance_services.start_progress)

    @action(detail=True, methods=["post"], url_path="wait-for-parts")
    def wait_for_parts(self, request, pk=None):
        return self._apply_transition(maintenance_services.wait_for_parts)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self._apply_transition(maintenance_services.complete)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        return self._apply_transition(maintenance_services.review)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        serializer = CloseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._apply_transition(
            maintenance_services.close, closure_notes=serializer.validated_data.get("closure_notes", "")
        )

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        maintenance_request = self.get_object()

        if request.method == "POST":
            serializer = MaintenanceCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                organization=self.request.organization,
                request=maintenance_request,
                author=request.user,
                created_by=request.user,
                updated_by=request.user,
            )
            return Response(serializer.data, status=201)

        comments = maintenance_request.comments.select_related("author")
        return Response(MaintenanceCommentSerializer(comments, many=True).data)

    @action(detail=True, methods=["get", "post"])
    def attachments(self, request, pk=None):
        maintenance_request = self.get_object()

        if request.method == "POST":
            serializer = MaintenanceAttachmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                organization=self.request.organization,
                request=maintenance_request,
                uploaded_by=request.user,
                created_by=request.user,
                updated_by=request.user,
            )
            return Response(serializer.data, status=201)

        attachments = maintenance_request.attachments.all()
        return Response(MaintenanceAttachmentSerializer(attachments, many=True).data)

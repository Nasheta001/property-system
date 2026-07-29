from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet
from apps.documents.models import Document
from apps.documents.serializers import DocumentSerializer


class DocumentViewSet(TenantScopedModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "landlord"
    queryset = Document.objects.select_related("property", "lease__unit", "tenant", "uploaded_by")
    filterset_fields = ["document_type", "property", "lease", "tenant"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            uploaded_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

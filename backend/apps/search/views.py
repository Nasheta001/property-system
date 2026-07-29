from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrganizationMember
from apps.documents.models import Document
from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment
from apps.properties.models import Property, Unit
from apps.tenants.models import TenantProfile

MIN_QUERY_LENGTH = 2
RESULTS_PER_TYPE = 5


class GlobalSearchView(APIView):
    """A single endpoint fanning a query out across every searchable model,
    each scoped to the caller's active organization. Deliberately simple —
    icontains lookups capped at a handful of results per type — rather
    than a search index; the portfolios this targets are small enough
    that this stays fast without one.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < MIN_QUERY_LENGTH:
            return Response({"query": query, "results": []})

        organization = request.organization
        results = []

        properties = Property.objects.filter(organization=organization).filter(
            Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query)
        )[:RESULTS_PER_TYPE]
        results += [
            {
                "type": "property",
                "id": str(item.id),
                "label": item.name,
                "sublabel": item.city or item.address,
                "link": "/properties",
            }
            for item in properties
        ]

        units = Unit.objects.filter(organization=organization, unit_number__icontains=query).select_related(
            "floor__building__property"
        )[:RESULTS_PER_TYPE]
        results += [
            {
                "type": "unit",
                "id": str(item.id),
                "label": f"Unit {item.unit_number}",
                "sublabel": item.floor.building.property.name,
                "link": "/properties",
            }
            for item in units
        ]

        tenants = TenantProfile.objects.filter(organization=organization).filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )[:RESULTS_PER_TYPE]
        results += [
            {
                "type": "tenant",
                "id": str(item.id),
                "label": item.full_name,
                "sublabel": item.email or item.phone_number,
                "link": "/tenants",
            }
            for item in tenants
        ]

        payments = Payment.objects.filter(organization=organization, receipt_number__icontains=query)[
            :RESULTS_PER_TYPE
        ]
        results += [
            {
                "type": "payment",
                "id": str(item.id),
                "label": f"Receipt {item.receipt_number}",
                "sublabel": str(item.amount),
                "link": "/payments",
            }
            for item in payments
        ]

        maintenance_requests = MaintenanceRequest.objects.filter(organization=organization, title__icontains=query)[
            :RESULTS_PER_TYPE
        ]
        results += [
            {
                "type": "maintenance",
                "id": str(item.id),
                "label": item.title,
                "sublabel": item.get_status_display(),
                "link": "/maintenance",
            }
            for item in maintenance_requests
        ]

        documents = Document.objects.filter(organization=organization, title__icontains=query)[:RESULTS_PER_TYPE]
        results += [
            {
                "type": "document",
                "id": str(item.id),
                "label": item.title,
                "sublabel": item.get_document_type_display(),
                "link": "/documents",
            }
            for item in documents
        ]

        return Response({"query": query, "results": results})

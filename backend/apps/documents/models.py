from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel
from apps.documents.validators import validate_document_file


class Document(OrganizationScopedModel):
    """A file attached to a property, lease, and/or tenant — a signed lease
    agreement, an ID copy, an inspection report, proof of insurance. All
    three links are optional and independent so a document can be scoped
    as narrowly or broadly as it actually applies.
    """

    class DocumentType(models.TextChoices):
        LEASE_AGREEMENT = "lease_agreement", "Lease Agreement"
        IDENTIFICATION = "identification", "Identification"
        PROOF_OF_PAYMENT = "proof_of_payment", "Proof of Payment"
        INSPECTION_REPORT = "inspection_report", "Inspection Report"
        INSURANCE = "insurance", "Insurance"
        CONTRACT = "contract", "Contract"
        OTHER = "other", "Other"

    property = models.ForeignKey(
        "properties.Property", related_name="documents", on_delete=models.CASCADE, null=True, blank=True
    )
    lease = models.ForeignKey(
        "leases.Lease", related_name="documents", on_delete=models.CASCADE, null=True, blank=True
    )
    tenant = models.ForeignKey(
        "tenants.TenantProfile", related_name="documents", on_delete=models.CASCADE, null=True, blank=True
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.SET_NULL, null=True, blank=True
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, default=DocumentType.OTHER)
    file = models.FileField(upload_to="documents/%Y/%m/", validators=[validate_document_file])

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [models.Index(fields=["organization", "document_type"])]

    def __str__(self):
        return self.title

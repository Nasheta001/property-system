import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import Document
from apps.organizations.models import Membership

pytestmark = pytest.mark.django_db


def test_owner_can_upload_document_linked_to_lease(authenticated_client, active_lease):
    pdf = SimpleUploadedFile("lease.pdf", b"%PDF-1.4 fake pdf bytes", content_type="application/pdf")

    response = authenticated_client.post(
        "/api/v1/documents/",
        {
            "title": "Signed lease agreement",
            "document_type": "lease_agreement",
            "lease": str(active_lease.id),
            "tenant": str(active_lease.tenant.id),
            "file": pdf,
        },
        format="multipart",
    )

    assert response.status_code == 201, response.data
    document = Document.objects.get(pk=response.data["id"])
    assert document.uploaded_by_id is not None
    assert response.data["tenant_name"] == active_lease.tenant.full_name
    assert response.data["unit_number"] == active_lease.unit.unit_number


def test_upload_rejects_unsupported_extension(authenticated_client):
    bad_file = SimpleUploadedFile("virus.exe", b"not-real", content_type="application/octet-stream")

    response = authenticated_client.post(
        "/api/v1/documents/", {"title": "Bad file", "file": bad_file}, format="multipart"
    )

    assert response.status_code == 400


def test_document_from_another_organization_is_rejected(authenticated_client, tenant_profile):
    from apps.organizations.models import Organization
    from apps.tenants.models import TenantProfile

    other_owner = tenant_profile.organization.owner.__class__.objects.create_user(
        email="doc-other-owner@example.com", password="TestPassword123!"
    )
    other_org = Organization.objects.create(name="Doc Other Org", owner=other_owner, created_by=other_owner)
    other_tenant = TenantProfile.objects.create(
        organization=other_org, first_name="Foreign", last_name="Tenant", phone_number="+254700000000", created_by=other_owner
    )

    pdf = SimpleUploadedFile("id.jpg", b"fake-bytes", content_type="image/jpeg")
    response = authenticated_client.post(
        "/api/v1/documents/",
        {"title": "ID copy", "tenant": str(other_tenant.id), "file": pdf},
        format="multipart",
    )

    assert response.status_code == 400
    assert "tenant" in response.data["error"]["details"]


def test_tenant_role_cannot_upload_document(make_client_for, make_membership, make_user):
    tenant_user = make_user(email="doc-tenant@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4", content_type="application/pdf")
    response = client.post("/api/v1/documents/", {"title": "Some doc", "file": pdf}, format="multipart")

    assert response.status_code == 403


def test_tenant_role_can_list_documents(make_client_for, make_membership, make_user, authenticated_client, active_lease):
    pdf = SimpleUploadedFile("lease.pdf", b"%PDF-1.4", content_type="application/pdf")
    authenticated_client.post(
        "/api/v1/documents/", {"title": "Lease PDF", "lease": str(active_lease.id), "file": pdf}, format="multipart"
    )

    tenant_user = make_user(email="doc-reader@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.get("/api/v1/documents/")

    assert response.status_code == 200
    assert response.data["count"] == 1

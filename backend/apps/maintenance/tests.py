import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.maintenance.models import MaintenanceRequest
from apps.maintenance.services import (
    MaintenanceTransitionError,
    accept,
    assign,
    close,
    complete,
    review,
    start_progress,
    verify,
    wait_for_parts,
)
from apps.organizations.models import Membership

pytestmark = pytest.mark.django_db


def _create_request(unit, owner_user, **overrides):
    defaults = {
        "organization": unit.organization,
        "unit": unit,
        "title": "Leaking kitchen tap",
        "category": MaintenanceRequest.Category.PLUMBING,
        "priority": MaintenanceRequest.Priority.MEDIUM,
        "created_by": owner_user,
    }
    defaults.update(overrides)
    return MaintenanceRequest.objects.create(**defaults)


def test_tenant_can_report_maintenance_request(make_client_for, make_membership, make_user, unit):
    tenant_user = make_user(email="reporter@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.post(
        "/api/v1/maintenance-requests/",
        {"unit": str(unit.id), "title": "Broken window latch", "category": "structural", "priority": "low"},
    )

    assert response.status_code == 201, response.data
    assert response.data["status"] == MaintenanceRequest.Status.REPORTED
    request_obj = MaintenanceRequest.objects.get(pk=response.data["id"])
    assert request_obj.reported_by_id == tenant_user.id


def test_tenant_cannot_verify_request(make_client_for, make_membership, make_user, unit, owner_user):
    request_obj = _create_request(unit, owner_user)
    tenant_user = make_user(email="reporter2@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.post(f"/api/v1/maintenance-requests/{request_obj.id}/verify/")

    assert response.status_code == 403


def test_full_workflow_happy_path(unit, vendor, owner_user):
    request_obj = _create_request(unit, owner_user)

    request_obj = verify(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.VERIFIED

    request_obj = assign(request_obj, owner_user, vendor)
    assert request_obj.status == MaintenanceRequest.Status.ASSIGNED
    assert request_obj.vendor_id == vendor.id
    assert request_obj.assigned_at is not None

    request_obj = accept(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.ACCEPTED

    request_obj = start_progress(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.IN_PROGRESS

    request_obj = wait_for_parts(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.WAITING_PARTS

    request_obj = start_progress(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.IN_PROGRESS

    request_obj = complete(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.COMPLETED
    assert request_obj.completed_at is not None

    request_obj = review(request_obj, owner_user)
    assert request_obj.status == MaintenanceRequest.Status.REVIEWED

    request_obj = close(request_obj, owner_user, closure_notes="Fixed and confirmed by tenant.")
    assert request_obj.status == MaintenanceRequest.Status.CLOSED
    assert request_obj.closure_notes == "Fixed and confirmed by tenant."


def test_cannot_skip_states(unit, vendor, owner_user):
    request_obj = _create_request(unit, owner_user)

    with pytest.raises(MaintenanceTransitionError):
        assign(request_obj, owner_user, vendor)

    with pytest.raises(MaintenanceTransitionError):
        complete(request_obj, owner_user)


def test_workflow_via_api(authenticated_client, unit, vendor, owner_user):
    request_obj = _create_request(unit, owner_user)
    base = f"/api/v1/maintenance-requests/{request_obj.id}"

    response = authenticated_client.post(f"{base}/verify/")
    assert response.status_code == 200
    assert response.data["status"] == "verified"

    response = authenticated_client.post(f"{base}/assign/", {"vendor": str(vendor.id)})
    assert response.status_code == 200
    assert response.data["status"] == "assigned"
    assert response.data["vendor_name"] == vendor.name

    response = authenticated_client.post(f"{base}/accept/")
    assert response.status_code == 200

    response = authenticated_client.post(f"{base}/start-progress/")
    assert response.status_code == 200
    assert response.data["status"] == "in_progress"

    response = authenticated_client.post(f"{base}/complete/")
    assert response.status_code == 200

    response = authenticated_client.post(f"{base}/review/")
    assert response.status_code == 200

    response = authenticated_client.post(f"{base}/close/", {"closure_notes": "All good."})
    assert response.status_code == 200
    assert response.data["status"] == "closed"
    assert response.data["closure_notes"] == "All good."


def test_tenant_can_add_comment(make_client_for, make_membership, make_user, unit, owner_user):
    request_obj = _create_request(unit, owner_user)
    tenant_user = make_user(email="commenter@example.com", first_name="Cee", last_name="Ommenter")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.post(
        f"/api/v1/maintenance-requests/{request_obj.id}/comments/", {"body": "Still leaking, please hurry."}
    )

    assert response.status_code == 201, response.data
    assert response.data["author_name"] == "Cee Ommenter"

    response = client.get(f"/api/v1/maintenance-requests/{request_obj.id}/comments/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_attachment_upload_accepts_image(authenticated_client, unit, owner_user):
    request_obj = _create_request(unit, owner_user)
    image = SimpleUploadedFile("leak.jpg", b"fake-image-bytes", content_type="image/jpeg")

    response = authenticated_client.post(
        f"/api/v1/maintenance-requests/{request_obj.id}/attachments/",
        {"file": image, "caption": "Leak under the sink"},
        format="multipart",
    )

    assert response.status_code == 201, response.data
    assert request_obj.attachments.count() == 1


def test_attachment_upload_rejects_unsupported_extension(authenticated_client, unit, owner_user):
    request_obj = _create_request(unit, owner_user)
    bad_file = SimpleUploadedFile("malware.exe", b"not-a-real-exe", content_type="application/octet-stream")

    response = authenticated_client.post(
        f"/api/v1/maintenance-requests/{request_obj.id}/attachments/",
        {"file": bad_file},
        format="multipart",
    )

    assert response.status_code == 400
    assert request_obj.attachments.count() == 0


def test_vendor_write_requires_landlord_role(make_client_for, make_membership, make_user):
    accountant = make_user(email="accountant2@example.com")
    make_membership(accountant, Membership.Role.ACCOUNTANT)
    client = make_client_for(accountant)

    response = client.post("/api/v1/vendors/", {"name": "New Vendor"})

    assert response.status_code == 403

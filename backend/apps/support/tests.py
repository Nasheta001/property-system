import pytest

from apps.organizations.models import Membership
from apps.support.models import SupportTicket, SupportTicketComment

pytestmark = pytest.mark.django_db


def test_org_member_can_create_and_read_ticket(authenticated_client, organization):
    response = authenticated_client.post(
        "/api/v1/support-tickets/",
        {"subject": "Billing question", "description": "Why was I charged twice?", "category": "billing"},
    )

    assert response.status_code == 201, response.data
    assert response.data["status"] == SupportTicket.Status.OPEN

    response = authenticated_client.get("/api/v1/support-tickets/")
    assert response.status_code == 200
    assert response.data["count"] == 1


def test_creator_can_close_own_ticket(make_client_for, make_membership, make_user, organization):
    reporter = make_user(email="ticket-reporter@example.com")
    make_membership(reporter, Membership.Role.TENANT)
    client = make_client_for(reporter)

    response = client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]

    response = client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    assert response.status_code == 200
    assert response.data["status"] == SupportTicket.Status.CLOSED


def test_other_member_cannot_close_someone_elses_ticket(
    make_client_for, make_membership, make_user, organization
):
    reporter = make_user(email="ticket-owner@example.com")
    make_membership(reporter, Membership.Role.TENANT)
    reporter_client = make_client_for(reporter)

    response = reporter_client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]

    bystander = make_user(email="ticket-bystander@example.com")
    make_membership(bystander, Membership.Role.TENANT)
    bystander_client = make_client_for(bystander)

    response = bystander_client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    assert response.status_code == 403


def test_landlord_can_close_any_ticket_in_org(make_client_for, make_membership, make_user, organization):
    reporter = make_user(email="ticket-reporter2@example.com")
    make_membership(reporter, Membership.Role.TENANT)
    reporter_client = make_client_for(reporter)

    response = reporter_client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]

    landlord = make_user(email="ticket-landlord@example.com")
    make_membership(landlord, Membership.Role.LANDLORD)
    landlord_client = make_client_for(landlord)

    response = landlord_client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    assert response.status_code == 200


def test_reopen_closed_ticket(authenticated_client, organization):
    response = authenticated_client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]
    authenticated_client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    response = authenticated_client.post(f"/api/v1/support-tickets/{ticket_id}/reopen/")

    assert response.status_code == 200
    assert response.data["status"] == SupportTicket.Status.OPEN


def test_cannot_close_already_closed_ticket(authenticated_client, organization):
    response = authenticated_client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]
    authenticated_client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    response = authenticated_client.post(f"/api/v1/support-tickets/{ticket_id}/close/")

    assert response.status_code == 400


def test_comments_endpoint_hides_internal_notes(authenticated_client, organization, owner_user):
    response = authenticated_client.post("/api/v1/support-tickets/", {"subject": "Help", "description": "..."})
    ticket_id = response.data["id"]
    ticket = SupportTicket.objects.get(pk=ticket_id)

    SupportTicketComment.objects.create(
        organization=organization, ticket=ticket, author=owner_user, body="Internal-only note", is_internal=True,
        created_by=owner_user,
    )

    response = authenticated_client.post(f"/api/v1/support-tickets/{ticket_id}/comments/", {"body": "Public reply"})
    assert response.status_code == 201

    response = authenticated_client.get(f"/api/v1/support-tickets/{ticket_id}/comments/")
    assert response.status_code == 200
    bodies = [comment["body"] for comment in response.data]
    assert "Public reply" in bodies
    assert "Internal-only note" not in bodies

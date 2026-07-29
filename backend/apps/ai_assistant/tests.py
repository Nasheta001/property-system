import httpx
import pytest

from apps.ai_assistant.models import AIConversation
from apps.ai_assistant.services import AnthropicProvider, RuleBasedProvider, get_provider

pytestmark = pytest.mark.django_db


def test_start_conversation_creates_conversation_and_answers(authenticated_client, organization):
    response = authenticated_client.post("/api/v1/ai/conversations/start/", {"question": "How are we doing overall?"})

    assert response.status_code == 201
    assert response.data["message"]["role"] == "assistant"
    assert response.data["message"]["provider"] == "rule_based"
    assert response.data["conversation"]["title"] == "How are we doing overall?"
    assert AIConversation.objects.filter(organization=organization).count() == 1


def test_rule_based_overdue_rent_answers_from_data(authenticated_client, active_lease):
    response = authenticated_client.post(
        "/api/v1/ai/conversations/start/", {"question": "Do we have any overdue rent?"}
    )

    assert response.status_code == 201
    assert active_lease.tenant.full_name in response.data["message"]["content"]


def test_rule_based_vacancy_answers_from_data(authenticated_client, unit):
    response = authenticated_client.post("/api/v1/ai/conversations/start/", {"question": "What's our occupancy?"})

    assert response.status_code == 201
    assert "occupied" in response.data["message"]["content"].lower()


def test_follow_up_question_appends_to_same_conversation(authenticated_client):
    start = authenticated_client.post("/api/v1/ai/conversations/start/", {"question": "Give me a summary."})
    conversation_id = start.data["conversation"]["id"]

    response = authenticated_client.post(
        f"/api/v1/ai/conversations/{conversation_id}/messages/", {"question": "What about maintenance?"}
    )

    assert response.status_code == 201
    history = authenticated_client.get(f"/api/v1/ai/conversations/{conversation_id}/messages/")
    assert len(history.data) == 4  # user, assistant, user, assistant


def test_conversation_is_scoped_to_asking_user(make_client_for, make_user, make_membership, authenticated_client):
    start = authenticated_client.post("/api/v1/ai/conversations/start/", {"question": "Give me a summary."})
    conversation_id = start.data["conversation"]["id"]

    other_member = make_user(email="other-member@example.com")
    make_membership(other_member, "property_manager")
    other_client = make_client_for(other_member)

    response = other_client.get(f"/api/v1/ai/conversations/{conversation_id}/messages/")
    assert response.status_code == 404

    listing = other_client.get("/api/v1/ai/conversations/")
    assert listing.data["count"] == 0


def test_ask_requires_organization_membership(api_client, owner_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.post("/api/v1/ai/conversations/start/", {"question": "Hello?"})
    assert response.status_code == 403


def test_get_provider_falls_back_to_rule_based_without_api_key(settings):
    settings.ANTHROPIC_API_KEY = ""
    assert isinstance(get_provider(), RuleBasedProvider)


def test_get_provider_uses_anthropic_when_key_configured(settings):
    settings.ANTHROPIC_API_KEY = "fake-test-key"
    settings.AI_ASSISTANT_MODEL = "claude-sonnet-5"
    provider = get_provider()
    assert isinstance(provider, AnthropicProvider)
    assert provider.api_key == "fake-test-key"


def test_anthropic_provider_handles_http_error_gracefully(monkeypatch, organization):
    def raise_error(*args, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx, "post", raise_error)

    provider = AnthropicProvider(api_key="fake-key", model="claude-sonnet-5")
    answer = provider.respond(organization, "Hello?", [{"role": "user", "content": "Hello?"}])

    assert "temporarily unavailable" in answer

import logging

import httpx
from django.conf import settings

from apps.ai_assistant import analytics
from apps.ai_assistant.models import AIConversation, AIMessage

logger = logging.getLogger("apps.ai_assistant")

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
REQUEST_TIMEOUT_SECONDS = 20

# (keywords, handler) — checked in order, first match wins.
INTENTS = [
    (("overdue", "late rent", "unpaid", "arrears"), analytics.overdue_rent_summary),
    (("vacan", "empty unit", "occupancy", "occupied"), analytics.vacancy_summary),
    (("maintenance", "repair", "work order"), analytics.maintenance_summary),
    (("expir", "ending soon", "renew"), analytics.lease_expiration_summary),
    (("revenue", "income", "collected", "rent collected"), analytics.revenue_summary),
    (("summary", "overview", "snapshot", "how are we doing"), analytics.organization_snapshot),
]

FALLBACK_HELP = (
    "I can currently answer questions about: overdue rent, vacancy/occupancy, "
    "open maintenance requests, upcoming lease expirations, rent collected this month, "
    "and a general organization summary. Try asking one of those, or connect an "
    "ANTHROPIC_API_KEY to unlock free-form questions."
)


class AIProvider:
    name = "base"

    def respond(self, organization, question, history):
        raise NotImplementedError


class RuleBasedProvider(AIProvider):
    """The default provider — no external API call, no network dependency.
    Matches the question against a fixed set of intents and answers from
    the organization's live data via `apps.ai_assistant.analytics`.
    """

    name = "rule_based"

    def respond(self, organization, question, history):
        lowered = question.lower()
        for keywords, handler in INTENTS:
            if any(keyword in lowered for keyword in keywords):
                return handler(organization)
        return FALLBACK_HELP


class AnthropicProvider(AIProvider):
    """Calls the Anthropic Messages API directly over HTTP, grounded with a
    live data snapshot of the organization so answers can't drift from
    what's actually in the database. This is the real, functioning
    production hookup — it's simply inert until ANTHROPIC_API_KEY is set.
    """

    name = "anthropic"

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def respond(self, organization, question, history):
        """`history` already ends with the current question (see `ask()`,
        which persists the user message before calling the provider), so
        it becomes the full message list — nothing is appended here.
        """
        system_prompt = (
            "You are the AI assistant embedded in Property System, a property management "
            "platform. Answer the user's question about their organization using ONLY the "
            "data snapshot below. If the answer isn't in the snapshot, say you don't have "
            "that information rather than guessing.\n\n" + analytics.organization_snapshot(organization)
        )
        messages = [{"role": entry["role"], "content": entry["content"]} for entry in history]

        try:
            response = httpx.post(
                ANTHROPIC_MESSAGES_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": ANTHROPIC_API_VERSION,
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": messages,
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
            return "".join(block.get("text", "") for block in payload.get("content", []))
        except httpx.HTTPError:
            logger.exception("Anthropic API call failed")
            return "The AI provider is temporarily unavailable. Please try again shortly."


def get_provider():
    if settings.ANTHROPIC_API_KEY:
        return AnthropicProvider(settings.ANTHROPIC_API_KEY, settings.AI_ASSISTANT_MODEL)
    return RuleBasedProvider()


def ask(organization, user, conversation, question):
    AIMessage.objects.create(
        organization=organization,
        conversation=conversation,
        role=AIMessage.Role.USER,
        content=question,
        created_by=user,
        updated_by=user,
    )

    history = list(conversation.messages.order_by("created_at").values("role", "content"))
    provider = get_provider()
    answer = provider.respond(organization, question, history)

    if not conversation.title:
        conversation.title = question[:80]
        conversation.save(update_fields=["title"])

    return AIMessage.objects.create(
        organization=organization,
        conversation=conversation,
        role=AIMessage.Role.ASSISTANT,
        content=answer,
        provider=provider.name,
        created_by=user,
        updated_by=user,
    )


def start_conversation(organization, user, question):
    conversation = AIConversation.objects.create(
        organization=organization, started_by=user, created_by=user, updated_by=user
    )
    message = ask(organization, user, conversation, question)
    return conversation, message

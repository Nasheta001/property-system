from django.conf import settings
from django.db import models

from apps.core.models import OrganizationScopedModel


class AIConversation(OrganizationScopedModel):
    """A thread of questions a single user has asked the assistant about
    their organization. Scoped to the asking user (not shared across the
    org) — this is a personal working tool, not a team discussion.
    """

    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, help_text="Auto-set from the first question asked.")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "AI Conversation"
        verbose_name_plural = "AI Conversations"
        indexes = [models.Index(fields=["organization", "started_by"])]

    def __str__(self):
        return self.title or f"Conversation {self.id}"


class AIMessage(OrganizationScopedModel):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(AIConversation, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    provider = models.CharField(
        max_length=20, blank=True, help_text="Which provider produced this message, e.g. 'anthropic' or 'rule_based'."
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "AI Message"
        verbose_name_plural = "AI Messages"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

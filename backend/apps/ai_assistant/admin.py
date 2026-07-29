from django.contrib import admin

from apps.ai_assistant.models import AIConversation, AIMessage


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    fields = ["role", "content", "provider", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "started_by", "created_at"]
    search_fields = ["title", "organization__name", "started_by__email"]
    autocomplete_fields = ["organization", "started_by"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [AIMessageInline]

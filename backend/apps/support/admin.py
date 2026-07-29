from django.contrib import admin

from apps.support.models import SupportTicket, SupportTicketComment


class SupportTicketCommentInline(admin.TabularInline):
    model = SupportTicketComment
    extra = 0
    fields = ["author", "body", "is_internal", "created_at"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["author"]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """The platform support team's working view: every organization's
    tickets in one place (Django admin isn't tenant-scoped for staff),
    with assignment and status change handled right here alongside
    internal-only notes via the comment inline.
    """

    list_display = ["subject", "organization", "category", "priority", "status", "assigned_to", "created_at"]
    list_filter = ["status", "category", "priority"]
    search_fields = ["subject", "description", "organization__name"]
    autocomplete_fields = ["organization", "assigned_to"]
    readonly_fields = ["id", "created_by", "resolved_at", "closed_at", "created_at", "updated_at"]
    inlines = [SupportTicketCommentInline]


@admin.register(SupportTicketComment)
class SupportTicketCommentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "author", "is_internal", "created_at"]
    list_filter = ["is_internal"]
    search_fields = ["body", "ticket__subject"]
    autocomplete_fields = ["organization", "ticket", "author"]
    readonly_fields = ["id", "created_at", "updated_at"]

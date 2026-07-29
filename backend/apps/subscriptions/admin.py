from django.contrib import admin

from apps.subscriptions.models import SubscriptionEvent


@admin.register(SubscriptionEvent)
class SubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ["organization", "previous_plan", "new_plan", "changed_by", "created_at"]
    list_filter = ["previous_plan", "new_plan"]
    search_fields = ["organization__name", "reason"]
    autocomplete_fields = ["organization", "changed_by"]
    readonly_fields = ["id", "organization", "previous_plan", "new_plan", "changed_by", "reason", "created_at", "updated_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

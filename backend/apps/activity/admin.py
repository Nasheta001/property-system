from django.contrib import admin

from apps.activity.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["actor_name", "verb", "organization", "target_type", "created_at"]
    list_filter = ["target_type"]
    search_fields = ["actor_name", "verb"]
    autocomplete_fields = ["organization", "actor"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

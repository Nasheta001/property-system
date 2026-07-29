from django.contrib import admin

from apps.tenants.models import TenantProfile


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "organization", "email", "phone_number", "created_at"]
    list_filter = ["organization"]
    search_fields = ["first_name", "last_name", "email", "phone_number", "national_id"]
    autocomplete_fields = ["organization", "user"]
    readonly_fields = ["id", "created_at", "updated_at"]

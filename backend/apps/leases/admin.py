from django.contrib import admin

from apps.leases.models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ["tenant", "unit", "status", "start_date", "end_date", "rent_amount", "created_at"]
    list_filter = ["status"]
    search_fields = ["unit__unit_number", "tenant__first_name", "tenant__last_name"]
    autocomplete_fields = ["organization", "unit", "tenant"]
    readonly_fields = ["id", "signed_at", "terminated_at", "created_at", "updated_at"]

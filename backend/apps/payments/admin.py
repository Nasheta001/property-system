from django.contrib import admin

from apps.payments.models import LedgerEntry, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "tenant", "lease", "amount", "method", "status", "payment_date"]
    list_filter = ["status", "method"]
    search_fields = ["receipt_number", "provider_reference", "tenant__first_name", "tenant__last_name"]
    autocomplete_fields = ["organization", "lease", "tenant"]
    readonly_fields = ["id", "receipt_number", "receipt_sent_at", "created_at", "updated_at"]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ["entry_type", "lease", "amount", "payment", "created_at"]
    list_filter = ["entry_type"]
    search_fields = ["lease__unit__unit_number"]
    autocomplete_fields = ["organization", "lease", "payment"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

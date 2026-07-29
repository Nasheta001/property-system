from django.contrib import admin

from apps.maintenance.models import MaintenanceAttachment, MaintenanceComment, MaintenanceRequest, Vendor


class MaintenanceCommentInline(admin.TabularInline):
    model = MaintenanceComment
    extra = 0
    fields = ["author", "body", "created_at"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["author"]


class MaintenanceAttachmentInline(admin.TabularInline):
    model = MaintenanceAttachment
    extra = 0
    fields = ["file", "caption", "uploaded_by"]
    autocomplete_fields = ["uploaded_by"]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "specialty", "phone_number", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "contact_person", "specialty"]
    autocomplete_fields = ["organization"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "unit", "status", "priority", "category", "vendor", "created_at"]
    list_filter = ["status", "priority", "category"]
    search_fields = ["title", "description", "unit__unit_number"]
    autocomplete_fields = ["organization", "unit", "tenant", "reported_by", "vendor"]
    readonly_fields = [
        "id",
        "assigned_at",
        "accepted_at",
        "completed_at",
        "reviewed_at",
        "closed_at",
        "created_at",
        "updated_at",
    ]
    inlines = [MaintenanceCommentInline, MaintenanceAttachmentInline]

from django.contrib import admin

from apps.organizations.models import Membership, Organization


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ["user", "role", "is_active", "joined_at"]
    readonly_fields = ["joined_at"]
    autocomplete_fields = ["user"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subscription_plan", "is_active", "owner", "created_at"]
    list_filter = ["subscription_plan", "is_active"]
    search_fields = ["name", "slug", "email"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["user__email", "organization__name"]
    autocomplete_fields = ["user", "organization"]
    readonly_fields = ["id", "joined_at", "created_at", "updated_at"]

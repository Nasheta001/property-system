from django.db.models import Count, Q

from apps.activity.services import log_activity
from apps.organizations.models import Organization
from apps.subscriptions.catalog import PLAN_CATALOG
from apps.users.models import User


class OrganizationStatusError(Exception):
    pass


def annotated_organizations():
    return (
        Organization.objects.annotate(
            member_count=Count("memberships", filter=Q(memberships__is_active=True), distinct=True),
            property_count=Count("propertys", distinct=True),
            unit_count=Count("units", distinct=True),
        )
        .select_related("owner")
        .order_by("name")
    )


def suspend_organization(organization, staff_user, reason=""):
    if not organization.is_active:
        raise OrganizationStatusError("Organization is already suspended.")

    organization.is_active = False
    organization.updated_by = staff_user
    organization.save(update_fields=["is_active", "updated_by", "updated_at"])

    log_activity(
        organization,
        staff_user,
        f"suspended this organization{f' ({reason})' if reason else ''}",
        target_type="Organization",
        target_id=organization.id,
    )
    return organization


def reactivate_organization(organization, staff_user):
    if organization.is_active:
        raise OrganizationStatusError("Organization is already active.")

    organization.is_active = True
    organization.updated_by = staff_user
    organization.save(update_fields=["is_active", "updated_by", "updated_at"])

    log_activity(
        organization,
        staff_user,
        "reactivated this organization",
        target_type="Organization",
        target_id=organization.id,
    )
    return organization


def platform_stats():
    organizations = Organization.objects.all()
    active_organizations = organizations.filter(is_active=True)

    plan_counts = dict(
        active_organizations.values_list("subscription_plan").annotate(count=Count("id")).order_by()
    )
    plan_breakdown = [
        {"plan": code, "name": PLAN_CATALOG[code]["name"], "count": plan_counts.get(code, 0)}
        for code in PLAN_CATALOG
    ]
    mrr = sum(
        float(PLAN_CATALOG[code]["price_monthly"]) * count
        for code, count in plan_counts.items()
        if PLAN_CATALOG[code]["price_monthly"] is not None
    )

    counted_organizations = list(annotated_organizations())

    return {
        "total_organizations": organizations.count(),
        "active_organizations": active_organizations.count(),
        "suspended_organizations": organizations.filter(is_active=False).count(),
        "total_users": User.objects.count(),
        "total_properties": sum(org.property_count for org in counted_organizations),
        "total_units": sum(org.unit_count for org in counted_organizations),
        "plan_breakdown": plan_breakdown,
        "estimated_mrr": round(mrr, 2),
    }

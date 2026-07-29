from apps.organizations.models import Membership, Organization
from apps.properties.models import Property, Unit
from apps.subscriptions.catalog import PLAN_CATALOG, plan_limits
from apps.subscriptions.models import SubscriptionEvent


class SubscriptionPlanError(Exception):
    pass


def compute_usage(organization):
    return {
        "properties": Property.objects.filter(organization=organization).count(),
        "units": Unit.objects.filter(organization=organization).count(),
        "team_members": Membership.objects.filter(organization=organization, is_active=True).count(),
    }


def change_plan(organization, new_plan, user, reason=""):
    if new_plan not in PLAN_CATALOG:
        raise SubscriptionPlanError(f"'{new_plan}' is not a known subscription plan.")

    if new_plan == organization.subscription_plan:
        raise SubscriptionPlanError(f"Organization is already on the {new_plan} plan.")

    usage = compute_usage(organization)
    limits = plan_limits(new_plan)
    overages = [
        f"{count} {metric.replace('_', ' ')} exceeds the {new_plan} plan's limit of {limits[metric]}"
        for metric, count in (
            ("max_properties", usage["properties"]),
            ("max_units", usage["units"]),
            ("max_team_members", usage["team_members"]),
        )
        if limits[metric] is not None and count > limits[metric]
    ]
    if overages:
        raise SubscriptionPlanError(f"Cannot switch to {new_plan}: {'; '.join(overages)}.")

    previous_plan = organization.subscription_plan
    organization.subscription_plan = new_plan
    organization.updated_by = user
    organization.save(update_fields=["subscription_plan", "updated_by", "updated_at"])

    return SubscriptionEvent.objects.create(
        organization=organization,
        previous_plan=previous_plan,
        new_plan=new_plan,
        changed_by=user,
        reason=reason,
        created_by=user,
        updated_by=user,
    )

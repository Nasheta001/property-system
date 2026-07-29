"""The plan catalog is versioned in code, not the database — pricing and
limits are a product/deploy-time decision, not tenant data. This mirrors
`apps.core.permissions.ROLE_HIERARCHY`: a small fixed table other modules
read from, never mutated at runtime.
"""

from apps.organizations.models import Organization

PLAN_CATALOG = {
    Organization.SubscriptionPlan.TRIAL: {
        "code": Organization.SubscriptionPlan.TRIAL,
        "name": "Trial",
        "price_monthly": "0.00",
        "currency": "USD",
        "limits": {"max_properties": 1, "max_units": 10, "max_team_members": 3},
        "features": ["Core property management", "Up to 10 units", "Community support"],
    },
    Organization.SubscriptionPlan.STARTER: {
        "code": Organization.SubscriptionPlan.STARTER,
        "name": "Starter",
        "price_monthly": "29.00",
        "currency": "USD",
        "limits": {"max_properties": 3, "max_units": 50, "max_team_members": 10},
        "features": ["Everything in Trial", "Up to 50 units", "Email support"],
    },
    Organization.SubscriptionPlan.PROFESSIONAL: {
        "code": Organization.SubscriptionPlan.PROFESSIONAL,
        "name": "Professional",
        "price_monthly": "99.00",
        "currency": "USD",
        "limits": {"max_properties": 15, "max_units": 300, "max_team_members": 30},
        "features": ["Everything in Starter", "Up to 300 units", "Priority support", "Advanced reports"],
    },
    Organization.SubscriptionPlan.ENTERPRISE: {
        "code": Organization.SubscriptionPlan.ENTERPRISE,
        "name": "Enterprise",
        "price_monthly": None,
        "currency": "USD",
        "limits": {"max_properties": None, "max_units": None, "max_team_members": None},
        "features": ["Everything in Professional", "Unlimited units", "Dedicated support", "Custom contract"],
    },
}

PLAN_ORDER = [
    Organization.SubscriptionPlan.TRIAL,
    Organization.SubscriptionPlan.STARTER,
    Organization.SubscriptionPlan.PROFESSIONAL,
    Organization.SubscriptionPlan.ENTERPRISE,
]


def plan_list():
    return [PLAN_CATALOG[code] for code in PLAN_ORDER]


def plan_limits(plan_code):
    return PLAN_CATALOG[plan_code]["limits"]

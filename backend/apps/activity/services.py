from apps.activity.models import ActivityLog


def log_activity(organization, actor, verb, *, target_type="", target_id="", target_link=""):
    return ActivityLog.objects.create(
        organization=organization,
        actor=actor,
        actor_name=actor.full_name if actor else "System",
        verb=verb,
        target_type=target_type,
        target_id=str(target_id) if target_id else "",
        target_link=target_link,
    )

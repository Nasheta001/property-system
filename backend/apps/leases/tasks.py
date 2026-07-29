import logging

from celery import shared_task

logger = logging.getLogger("apps.leases")


@shared_task
def expire_leases():
    """Daily sweep: expires active leases past their end date and frees
    their units. See `apps.leases.services.expire_due_leases`.
    """
    from apps.leases.services import expire_due_leases

    count = expire_due_leases()
    logger.info("expire_leases: marked %s lease(s) as expired", count)
    return count

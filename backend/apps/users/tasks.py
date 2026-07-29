import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("apps.users")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    from apps.users.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_welcome_email: user %s no longer exists", user_id)
        return

    context = {"full_name": user.full_name, "frontend_url": settings.FRONTEND_URL}
    html_body = render_to_string("emails/welcome.html", context)

    try:
        send_mail(
            subject="Welcome to Property System",
            message=strip_tags(html_body),
            html_message=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001 - retry on any transient email failure
        raise self.retry(exc=exc)


@shared_task
def purge_expired_tokens():
    """Deletes expired/blacklisted JWT refresh tokens from the database so
    the outstanding-token table doesn't grow unbounded.
    """
    from django.core.management import call_command

    call_command("flushexpiredtokens")

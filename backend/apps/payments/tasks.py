import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger("apps.payments")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_receipt_email(self, payment_id):
    from apps.payments.models import Payment

    try:
        payment = Payment.objects.select_related("lease__unit", "tenant", "organization").get(pk=payment_id)
    except Payment.DoesNotExist:
        logger.warning("send_receipt_email: payment %s no longer exists", payment_id)
        return

    if not payment.tenant.email:
        logger.info("send_receipt_email: tenant %s has no email on file, skipping", payment.tenant_id)
        return

    context = {
        "tenant_name": payment.tenant.full_name,
        "organization_name": payment.organization.name,
        "unit_number": payment.lease.unit.unit_number,
        "amount": payment.amount,
        "currency": payment.organization.currency,
        "payment_date": payment.payment_date,
        "receipt_number": payment.receipt_number,
        "method": payment.get_method_display(),
    }
    html_body = render_to_string("emails/receipt.html", context)

    try:
        send_mail(
            subject=f"Receipt {payment.receipt_number}",
            message=strip_tags(html_body),
            html_message=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.tenant.email],
            fail_silently=False,
        )
        Payment.objects.filter(pk=payment.id).update(receipt_sent_at=timezone.now())
    except Exception as exc:  # noqa: BLE001 - retry on any transient email failure
        raise self.retry(exc=exc)

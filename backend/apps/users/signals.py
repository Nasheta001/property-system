from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User
from apps.users.tasks import send_welcome_email


@receiver(post_save, sender=User)
def dispatch_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_welcome_email.delay(str(instance.id))

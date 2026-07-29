import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("property_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "purge-expired-blacklisted-tokens": {
        "task": "apps.users.tasks.purge_expired_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    "expire-due-leases": {
        "task": "apps.leases.tasks.expire_leases",
        "schedule": crontab(hour=1, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Recorder.settings")
app = Celery("Recorder")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    'schedule_record_alerts': {
        'task': 'schedule_record_alerts',
        'schedule': crontab(hour='8'),
    }
}
app.autodiscover_tasks()

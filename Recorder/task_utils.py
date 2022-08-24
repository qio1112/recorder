from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from records.models import get_alert_info
from datetime import datetime
from Recorder.recorder_utils import get_current_milli
import json


@shared_task(name='send_email_task')
def send_email_task(subject, message, email_from, recipient_list):
    send_mail(subject, message, email_from, recipient_list)


def send_email_new_record(recipient, new_record):
    # send email
    email_from = settings.EMAIL_HOST_USER
    if email_from:
        subject = f'New Record Added: {new_record.title}'
        message = f'You posted a new record with title: {new_record.title} \n ' \
                  f'Labels: {[label.name for label in new_record.labels.all()]}'
        recipient_list = [recipient]
        send_email_task.delay(subject, message, email_from, recipient_list)
        print("New record email sent!")


def schedule_one_off_task(task_name, dt: datetime, args=None):
    clocked_schedule = ClockedSchedule.objects.create(
        clocked_time=dt
    )
    name = task_name + str(get_current_milli())
    PeriodicTask.objects.create(
        name=name,
        task=task_name,
        one_off=True,
        clocked_id=clocked_schedule.id,
        args=args
    )
    print(f'New task {name} scheduled at {str(dt)}')


def schedule_alert_email(record, dt: datetime):
    subject = 'Alert: ' + record.title
    message = f'Alert of record: {record.title} \n' \
              f'Labels: {[label.name for label in record.labels.all()]} \n\n\
              {record.content}'
    recipient_list = [record.created_by.email]
    email_from = settings.EMAIL_HOST_USER
    if email_from and recipient_list:
        schedule_one_off_task('send_email_task', dt, json.dumps([subject, message, email_from, recipient_list]))

# json.dumps({
#           'subject': subject,
#           'message':message,
#           'email_from':email_from,
#           'recipient_list': recipient_list}
#       )

@shared_task(name='schedule_record_alerts')
def schedule_record_alerts():
    alert_info = get_alert_info()
    for record, ts in alert_info:
        schedule_alert_email(record, ts)

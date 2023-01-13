from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from records.models import get_alert_info, add_record_downloading_option_chain
from datetime import datetime
from Recorder.recorder_utils import get_current_milli, read_secret_keys
from stock.option_chain import write_monitored_options_to_csv, get_option_chain_output_dir
from stock.stock_utils import is_trade_day, get_today
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


@shared_task(name='schedule_download_option_chain')
def schedule_download_option_chain(recipient: str):
    today = get_today()
    try:
        if is_trade_day(today):
            option_chain_output_dir = get_option_chain_output_dir()
            monitored_tickers = read_secret_keys()['OPTION_CHAIN_MONITORED_TICKERS'].split(',')
            print(f"Option Chain Output: {option_chain_output_dir}")
            print(f"Monitored Option Chain Symbols: {monitored_tickers}")
            if monitored_tickers:
                write_monitored_options_to_csv(option_chain_output_dir, monitored_tickers, dry_run=False)
                record = add_record_downloading_option_chain(today)
                # send_email_new_record(recipient, record)
    except Exception as e:
        print('Error:', e)
        send_email_task.delay('Writing option chain Failed', str(e), settings.EMAIL_HOST_USER, [recipient])
        raise e



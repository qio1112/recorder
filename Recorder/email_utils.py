from django.conf import settings
from django.core.mail import send_mail
from records.models import User, Record


def send_email_new_record(user, new_record):
    # send email
    email_from = settings.EMAIL_HOST_USER
    if email_from:
        subject = f'New Record Added: {new_record.title}'
        message = f'You posted a new record with title: {new_record.title} \n ' \
                  f'Labels: {[label.name for label in new_record.labels.all()]}'
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)
        print("New record email sent!")
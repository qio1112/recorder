from django.db import models
from Recorder.utils import LABEL_TYPE_CHOICES, LABEL_TYPE_DATE
from django.contrib.auth.models import User as AuthUser
from django.db.models import Q


class User(models.Model):
    user_name = models.CharField(max_length=100, primary_key=True)
    icon = models.ImageField(upload_to='records', null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    account_user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, null=True, related_name="shown_user")

    def __str__(self):
        return self.user_name


class Label(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    type = models.CharField(max_length=100, default="DEFAULT", choices=LABEL_TYPE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True)
    editable = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='labels')

    def removable(self):
        return "DATE" not in self.type and self.editable

    def can_be_edited_by(self, account_user):
        if not account_user:
            return False
        elif account_user.is_superuser:
            return True
        elif not self.removable():
            return False
        elif not self.created_by:
            return False
        else:
            shown_user = account_user.shown_user.get()
            return self.created_by.pk == shown_user.pk

    def __str__(self):
        return self.name


class Record(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records')
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True)
    labels = models.ManyToManyField(Label, related_name='records')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def can_be_edited_by(self, account_user):
        if not account_user:
            return False
        if account_user.is_superuser:
            return True
        else:
            shown_user = account_user.shown_user.get()
            return self.created_by.pk == shown_user.pk


class Picture(models.Model):
    picture = models.ImageField(upload_to='pictures')
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return f'{self.picture.name} in {self.record.title}'


def get_valid_record_by_user(account_user):
    if not account_user:
        return []
    if account_user.is_superuser:
        return Record.objects.all()
    else:
        shown_user = account_user.shown_user.get()
        return Record.objects.filter(Q(created_by=shown_user) | Q(is_public=True))


from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.db import models
from Recorder.utils import LABEL_TYPE_CHOICES, LABEL_TYPE_DATE
from django.contrib.auth.models import User as AuthUser
from django.db.models import Q
from django.templatetags.static import static
from Recorder.utils import PIPE, TAROT_NAMES, LABEL_TYPE_TAROT, reverse_tarot_name, \
    is_tarot_name, is_reversed_tarot_name
import json


class User(models.Model):
    user_name = models.CharField(max_length=100, primary_key=True)
    icon = models.ImageField(upload_to='records', null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    account_user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, null=True, related_name="shown_user")

    def __str__(self):
        return self.user_name


def label_name_validator(name):
    invalid_strings = [PIPE, '=', '[', ']', '{', '}', ',', '\'', '\"']
    if any(invalid_str in name for invalid_str in invalid_strings):
        raise ValidationError(f"Pipe '|' cannot be used in label names")


class Label(models.Model):
    name = models.CharField(max_length=100, primary_key=True, validators=[label_name_validator])
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

    def get_tarot_image(self):
        if self.type == LABEL_TYPE_TAROT and self.is_tarot_card():
            if self.is_revered_tarot_card():
                return static(f'tarot/{reverse_tarot_name(self.name)}.png')
            else:
                return static(f'tarot/{self.name}.png')
        return None

    def is_tarot_card(self):
        return is_tarot_name(self.name)

    def is_revered_tarot_card(self):
        return is_reversed_tarot_name(self.name)

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
    metadata = models.CharField(max_length=5000, null=True)

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

    def get_tarot_labels(self):
        return self.labels.filter(type=LABEL_TYPE_TAROT).all()

    def get_tarot_cards_ordered(self):
        tarot_labels = self.labels.filter(type=LABEL_TYPE_TAROT).all()
        tarot_cards = []
        for tarot_label in tarot_labels:
            if tarot_label.is_tarot_card():
                tarot_cards.append(tarot_label)
        tarot_name_label_dict = dict(zip([tarot_label.name for tarot_label in tarot_cards], tarot_cards))
        try:
            if self.metadata:
                print(f'metadata: {self.metadata}')
                metadata = json.loads(self.metadata)
                tarot_card_order = metadata['tarot_card_order']
                ordered = []
                if tarot_card_order and len(tarot_card_order) == len(tarot_cards):
                    for tarot_card_in_order in tarot_card_order:
                        if not tarot_name_label_dict.get(tarot_card_in_order):
                            raise ValueError(f"Invalid tarot order in metadata! {tarot_card_in_order}")
                        ordered.append(tarot_name_label_dict.get(tarot_card_in_order))
                return ordered
            else:
                return tarot_cards
        except JSONDecodeError as e:
            print(f"Cannot parse metadata json: {e}")
            return tarot_cards
        except ValueError:
            print(f"Invalid tarot order in metadata: {e}")
            return tarot_cards

    # TODO - update this method when more metadata added
    def update_metadata(self, new_meta):
        self.metadata = new_meta


class Picture(models.Model):
    picture = models.ImageField(upload_to='pictures')
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return f'{self.picture.name} in {self.record.title}'


# get records which the user has right to see
def get_valid_record_by_user(account_user):
    if not account_user:
        return []
    if account_user.is_superuser:
        return Record.objects.all()
    else:
        shown_user = account_user.shown_user.get()
        return Record.objects.filter(Q(created_by=shown_user) | Q(is_public=True))


def preload_tarot_labels():
    tarot_labels = []
    default_user = User.objects.get(user_name='Yipeng')
    for tarot_name in TAROT_NAMES:
        if not Label.objects.filter(pk=tarot_name).exists():
            tarot_labels.append(Label(name=tarot_name,
                                      type=LABEL_TYPE_TAROT,
                                      editable=False,
                                      created_by=default_user,
                                      last_modified_by=default_user))
        if not Label.objects.filter(pk=reverse_tarot_name(tarot_name)).exists():
            tarot_labels.append(Label(name=reverse_tarot_name(tarot_name),
                                      type=LABEL_TYPE_TAROT,
                                      editable=False,
                                      created_by=default_user,
                                      last_modified_by=default_user))
    return Label.objects.bulk_create(tarot_labels)

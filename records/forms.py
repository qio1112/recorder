from django import forms
from Recorder.utils import get_current_date_str, LABEL_TYPE_CHOICES
from .models import Label, Record, label_name_validator


class RecordFilterForm(forms.Form):
    filter_query = forms.CharField(max_length=200, label='record-filter')


class LabelForm(forms.Form):
    name = forms.CharField(max_length=100, label='label-name', validators=[label_name_validator])
    type = forms.ChoiceField(choices=LABEL_TYPE_CHOICES, label='label-type')


class RecordForm(forms.Form):
    title = forms.CharField(max_length=200)
    is_public = forms.BooleanField(initial=True, required=False)
    labels = forms.CharField(empty_value="")
    create_new_labels = forms.BooleanField(initial=True, required=False)
    content = forms.CharField(widget=forms.Textarea)
    images = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=False)
    delete_images = forms.MultipleChoiceField(required=False,
                                              widget=forms.CheckboxSelectMultiple)

    def __init__(self, delete_images=[], *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)
        # insert images related to the record if exist
        if delete_images:
            choices = []
            for image in delete_images:
                choices.append((image.id, image))
            self.fields['delete_images'].choices = choices


class RecordFilterForm(forms.Form):
    labels = forms.CharField(required=False)
    # author = forms.CharField(max_length=100)  # username of author



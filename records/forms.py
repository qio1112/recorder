from django import forms
from Recorder.recorder_utils import get_current_date_str, LABEL_TYPE_CHOICES
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
    rec_files = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}), required=False, label='Files')
    delete_files = forms.MultipleChoiceField(required=False,
                                              widget=forms.CheckboxSelectMultiple)
    metadata = forms.CharField(empty_value="", required=False, max_length=5000)

    def __init__(self, delete_images=None, delete_files=None, *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)
        # insert images related to the record if exist

        if delete_images:
            delete_image_choices = []
            for image in delete_images:
                delete_image_choices.append((image.id, image))
            self.fields['delete_images'].choices = delete_image_choices

        if delete_files:
            delete_file_choices = []
            for file in delete_files:
                delete_file_choices.append((file.id, file))
            self.fields['delete_files'].choices = delete_file_choices


class RecordFilterForm(forms.Form):
    labels = forms.CharField(required=False)
    record_title = forms.CharField(required=False)
    # author = forms.CharField(max_length=100)  # username of author



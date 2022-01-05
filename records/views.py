from json import JSONDecodeError

from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView
from django.db.models import Q
import json

import logging

from .models import Record, Label, User, Picture, get_valid_record_by_user
from .forms import RecordFilterForm, LabelForm, RecordForm
from Recorder.utils import get_current_date_str, PIPE, is_date, LABEL_TYPE_DEFAULT, LABEL_TYPE_DATE

logger = logging.getLogger("records.view")


# "/records"
class IndexPageView(View):

    def get(self, request):
        # get latest three records
        print(f"shown_user: {request.user.shown_user.get()}")
        print(f"super: {request.user.is_superuser}")
        latest_records = get_valid_record_by_user(request.user).order_by('-last_modified_date')[:6]
        # get at most three records with label of today
        today = get_current_date_str()
        print(today)
        today_records = get_valid_record_by_user(request.user).filter(labels__name=today).filter(labels__type='DATE')
        context = {
            'latest_records': latest_records,
            'today_records': today_records
        }
        return render(request, 'records/records_index.html', context)


# "/records/edit-label?label-name=<label-name>"
# do we need to edit a label? maybe changing the public flag
class EditLabelView(View):

    def get(self, request):
        pass

    def post(self, request):
        pass


# '/records/edit-record?record-id=<label-id>'
class EditRecordView(View):

    def get(self, request, record_id):
        if not Record.objects.filter(pk=record_id).exists():
            return redirect(reverse('add-record'))
        record = Record.objects.get(pk=record_id)
        account_user = request.user
        if not record.can_be_edited_by(account_user):
            return redirect(reverse('record-detail', args=[record_id]))
        existing_labels = Label.objects.order_by('name').only('name').all()
        existing_labels_names = [label.name for label in existing_labels]
        existing_images = record.pictures.all()
        used_labels = record.labels.order_by('name').only('name').all()
        record_form = RecordForm(delete_images=existing_images,
                                 initial={'title': record.title,
                                          'is_public': record.is_public,
                                          'labels': '',
                                          'create_new_labels': True,
                                          'content': record.content
                                          })
        return render(request, 'records/add_edit_record.html', {'form': record_form,
                                                                'title': 'Edit Record',
                                                                'existing_labels': existing_labels_names,
                                                                'used_labels': used_labels,
                                                                'record_id': record.id})

    def post(self, request, record_id):
        if not Record.objects.filter(pk=record_id).exists():
            return redirect(reverse('add-record'))
        record = Record.objects.get(pk=record_id)
        account_user = request.user
        if not record.can_be_edited_by(account_user):
            return redirect(reverse('record-detail', args=[record_id]))

        record_form = RecordForm(record.pictures.all(), request.POST, request.FILES)
        if record_form.is_valid():
            result = add_labels_from_record_form(record_form, "Add New Record", request, add_current_date=False)
            if not result['valid']:
                return result['response']
            all_labels = result['labels']
            record.labels.clear()
            for label in all_labels:
                record.labels.add(label)

            record.title = record_form.cleaned_data['title']
            record.is_public = record_form.cleaned_data['is_public']
            record.content = record_form.cleaned_data['content']

            delete_image_ids = record_form.cleaned_data['delete_images']
            for delete_image_id in delete_image_ids:
                Picture.objects.get(pk=delete_image_id).delete()

            # images
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    Picture.objects.create(picture=image, record=record)

            record.save()
        return redirect(reverse('record-detail', args=[record.id]))


# '/records/add-record'
class AddRecordView(View):

    def get(self, request):
        existing_labels = Label.objects.order_by('name').only('name').all()
        existing_labels_names = [label.name for label in existing_labels]
        return render(request, 'records/add_edit_record.html', {'form': RecordForm(),
                                                                'title': "Add New Record",
                                                                'existing_labels': existing_labels_names,
                                                                'post_url': reverse('add-record')})

    def post(self, request, *args, **kwargs):
        new_record_form = RecordForm([], request.POST, request.FILES)
        if new_record_form.is_valid():
            # labels
            result = add_labels_from_record_form(new_record_form, "Add New Record", request)
            if not result['valid']:
                return result['response']
            all_labels = result['labels']
            user = request.user.shown_user.get()
            new_record = Record.objects.create(title=new_record_form.cleaned_data['title'],
                                               content=new_record_form.cleaned_data['content'],
                                               created_by=user)

            for label in Label.objects.filter(name__in=all_labels):
                new_record.labels.add(label)

            # images
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    Picture.objects.create(picture=image, record=new_record)

            new_record.save()
            return redirect(reverse('record-detail', args=[new_record.id]))
        else:
            print(f"Add Record POST: invalid form, {new_record_form.errors}")
            return redirect(reverse('add-record'))


# "/records/add-label"
class AddLabelView(View):

    def get(self, request):
        form = LabelForm()
        context = {
            "form": form,
            "succeeded": False
        }
        return render(request, 'records/add_label.html', context)

    def post(self, request, *args, **kwargs):
        new_label_form = LabelForm(request.POST)
        succeeded = False
        if new_label_form.is_valid():
            user = request.user.shown_user.get()
            label_name = new_label_form.cleaned_data['name']
            if not Label.objects.filter(pk=label_name).exists():
                new_label = Label(name=label_name,
                                  type=new_label_form.cleaned_data['type'],
                                  editable=True,
                                  created_by=user,
                                  last_modified_by=user
                                  )
                new_label.save()
            else:
                new_label_form.add_error('name', f'Label {label_name} Already Exists!')
                succeeded = False
        if succeeded:
            form = LabelForm()
        else:
            form = new_label_form
        context = {
            "form": form,
            'succeeded': succeeded
        }
        return render(request, 'records/add_label.html', context)


class DeleteLabelView(View):

    def get(self, request, label_name):
        if label_name:
            label = Label.objects.get(name=label_name)
            account_user = request.user
            if label and label.can_be_edited_by(account_user):
                label.delete()
                logger.info(f"Delete Label with name: {label_name}")
        return redirect(reverse('labels'))


class DeleteRecordView(View):

    def get(self, request, record_id):
        if record_id:
            account_user = request.user
            record = Record.objects.get(pk=record_id)
            if not record.can_be_edited_by(account_user):
                return redirect(reverse('record-detail', args=[record_id]))
            if record:
                record.delete()
                logger.info(f"Delete Record with id: {record_id}")
        return redirect(reverse('records'))


# '/records/labels'
class LabelsView(ListView):
    template_name = 'records/all_labels.html'
    model = Label
    ordering = ["name"]
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_deletable = {}
        account_user = self.request.user
        for label in context['label_list']:
            is_deletable[label] = label.can_be_edited_by(account_user)
        context['is_deletable'] = is_deletable
        return context


# 'records/records'
class RecordsView(ListView):
    template_name = 'records/all_records.html'
    model = Record
    ordering = ["last_modified_date", "title"]
    paginate_by = 9

    def filter_selected_label_names(self):
        labels_query = self.request.GET.get('labels', '')
        label_names = []
        if labels_query:
            try:
                label_names = json.loads(labels_query)
            except JSONDecodeError:
                # in this case it's a single label query
                label_names = [labels_query]
        return label_names

    def get_queryset(self):
        labels_query = self.request.GET.get('labels', '')
        selected_label_names = self.filter_selected_label_names()
        # order = self.request.GET.get('orderby', 'give-default-value')
        new_context = get_valid_record_by_user(self.request.user)
        if selected_label_names:
            for label_name in selected_label_names:
                new_context = new_context.filter(
                    labels__name__exact=label_name,
                )
        return new_context.order_by("last_modified_date", "title")

    # def post(self, request, *args, **kwargs):
    #     record_filter_form = RecordFilterForm(request.POST)
    #     filter_query = ""
    #     if record_filter_form.is_valid():
    #         label_names = record_filter_form.cleaned_data['labels']
    #         print(f"label_names: {label_names}")
    #         if label_names:
    #             filter_query = "?labels=" + label_names
    #     return redirect(reverse('records') + filter_query)

    def get_context_data(self, **kwargs):
        context = super(RecordsView, self).get_context_data(**kwargs)
        context['records_filter_query'] = RecordFilterForm()
        # context['filter'] = self.request.GET.get('filter', '')
        # context['orderby'] = self.request.GET.get('orderby', 'give-default-value')
        labels = Label.objects.order_by('name').only('name').all()
        label_names = [label.name for label in labels]
        selected_label_names = self.filter_selected_label_names()
        context['labels'] = label_names
        context['selected_labels'] = selected_label_names
        return context


class RecordDetailView(View):

    def get(self, request, record_id):
        record = Record.objects.get(id=record_id)
        account_user = request.user
        can_edit = record.can_be_edited_by(account_user)
        context = {'record': record, 'can_edit': can_edit}
        return render(request, "records/record_detail.html", context)


def add_labels_from_record_form(valid_record_form, title, request, add_current_date=True):
    # labels
    labels_str = valid_record_form.cleaned_data['labels']
    label_names = json.loads(labels_str)
    create_new_labels = valid_record_form.cleaned_data['create_new_labels']
    nonexistent_labels = set()
    all_labels = set()
    for label in label_names:
        all_labels.add(label)
        if not Label.objects.filter(name=label).exists():
            nonexistent_labels.add(label)
    if (not create_new_labels) and nonexistent_labels:
        valid_record_form.add_error('labels', f"These labels do not exist: {' ,'.join(nonexistent_labels)}")
        response = render(request, 'records/add_edit_record.html', {"form": valid_record_form,
                                                                    "title": title})
        return {'valid': False, 'response': response}

    user = request.user.shown_user.get()
    for new_label_name in nonexistent_labels:
        if is_date(new_label_name):
            label_type = LABEL_TYPE_DATE
        else:
            label_type = LABEL_TYPE_DEFAULT
        Label.objects.create(name=new_label_name,
                             type=label_type,
                             created_by=user,
                             last_modified_by=user)
    # current date label is always there
    if add_current_date:
        current_date = get_current_date_str()
        if not Label.objects.filter(name=current_date).exists():
            Label.objects.create(name=current_date,
                                 type=LABEL_TYPE_DATE,
                                 created_by=user,
                                 last_modified_by=user)
        all_labels.add(current_date)
    return {'valid': True, 'labels': all_labels}

from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView
from django.db.models import Count
from Recorder.task_utils import send_email_new_record
import json

import logging

from .models import Record, Label, Picture, RecFile,  get_valid_record_by_user
from .forms import RecordFilterForm, LabelForm, RecordForm
from Recorder.recorder_utils import get_current_date_str, is_date, LABEL_TYPE_DEFAULT, LABEL_TYPE_DATE, LABEL_TYPE_TAROT, EXPENSES_LABEL

from .expenses import ExpensesProcessor

logger = logging.getLogger("records.view")
logging.basicConfig(level=logging.INFO)


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
        today_records = get_valid_record_by_user(request.user).filter(labels__name=today, labels__type='DATE')
        print(today_records)
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
        # existing_labels = Label.objects.order_by('name').only('name').all()
        existing_labels = Label.objects.annotate(num_records=Count('records')).order_by('num_records').all()[:100]
        existing_labels_names = [label.name for label in existing_labels]
        # tarot_labels = Label.objects.filter(type='TAROT').only('name').all()
        # tarot_label_names = [label.name for label in tarot_labels]
        tarot_label_names = []
        for label in existing_labels:
            if label.type == LABEL_TYPE_TAROT:
                tarot_label_names.append(label.name)
        existing_images = record.pictures.all()
        existing_files = record.files.all()
        used_labels = record.labels.order_by('type').all()
        record_form = RecordForm(delete_images=existing_images,
                                 delete_files=existing_files,
                                 initial={'title': record.title,
                                          'is_public': record.is_public,
                                          'labels': '',
                                          'create_new_labels': True,
                                          'content': record.content,
                                          })

        return render(request, 'records/add_edit_record.html', {'form': record_form,
                                                                'title': 'Edit Record',
                                                                'existing_labels': existing_labels_names,
                                                                'tarot_labels': tarot_label_names,
                                                                'used_tarot_card_labels': record.get_tarot_cards_ordered(),
                                                                'used_labels': used_labels,
                                                                'record_id': record.id})

    def post(self, request, record_id):
        if not Record.objects.filter(pk=record_id).exists():
            return redirect(reverse('add-record'))
        record = Record.objects.get(pk=record_id)
        account_user = request.user
        if not record.can_be_edited_by(account_user):
            return redirect(reverse('record-detail', args=[record_id]))

        record_form = RecordForm(record.pictures.all(), record.files.all(), request.POST, request.FILES)
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
            record.update_metadata(record_form.cleaned_data['metadata'])

            delete_image_ids = record_form.cleaned_data['delete_images']
            for delete_image_id in delete_image_ids:
                Picture.objects.get(pk=delete_image_id).delete()

            delete_file_ids = record_form.cleaned_data['delete_files']
            for delete_file_id in delete_file_ids:
                RecFile.objects.get(pk=delete_file_id).delete()

            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    Picture.objects.create(picture=image, record=record)

            files = request.FILES.getlist('rec_files')
            if files:
                for file in files:
                    RecFile.objects.create(file=file, record=record)

            record.save()
        return redirect(reverse('record-detail', args=[record.id]))


# '/records/add-record'
class AddRecordView(View):

    def get(self, request):
        existing_labels = Label.objects.annotate(num_records=Count('records')).order_by('num_records').all()[:100]
        existing_labels_names = sorted([label.name for label in existing_labels])
        # tarot_labels = Label.objects.filter(type='TAROT').all()
        # tarot_label_names = [label.name for label in tarot_labels]
        tarot_label_names = []
        for label in existing_labels:
            if label.type == LABEL_TYPE_TAROT:
                tarot_label_names.append(label.name)
        return render(request, 'records/add_edit_record.html', {'form': RecordForm(),
                                                                'title': "Add New Record",
                                                                'existing_labels': existing_labels_names,
                                                                'tarot_labels': tarot_label_names,
                                                                'post_url': reverse('add-record')
                                                                })

    def post(self, request, *args, **kwargs):
        new_record_form = RecordForm([], [], request.POST, request.FILES)
        if new_record_form.is_valid():
            # labels
            result = add_labels_from_record_form(new_record_form, "Add New Record", request)
            if not result['valid']:
                return result['response']
            all_labels = result['labels']
            user = request.user.shown_user.get()
            new_record = Record.objects.create(title=new_record_form.cleaned_data['title'],
                                               content=new_record_form.cleaned_data['content'],
                                               created_by=user,
                                               metadata=new_record_form.cleaned_data['metadata'])

            for label in Label.objects.filter(name__in=all_labels):
                new_record.labels.add(label)

            # images
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    Picture.objects.create(picture=image, record=new_record)

            files = request.FILES.getlist('rec_files')
            if files:
                for file in files:
                    RecFile.objects.create(file=file, record=new_record)

            new_record.save()
            # send email
            if user.email:
                send_email_new_record(user.email, new_record)

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
                succeeded = True
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
    ordering = ["type", "name"]
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
        selected_record_name_fraction = self.request.GET.get('record-title', '')

        # order = self.request.GET.get('orderby', 'give-default-value')
        new_context = get_valid_record_by_user(self.request.user)
        if selected_label_names:
            for label_name in selected_label_names:
                new_context = new_context.filter(
                    labels__name__exact=label_name,
                )
        if selected_record_name_fraction:
            new_context = new_context.filter(
                title__icontains=selected_record_name_fraction
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
        default_type_labels = Label.objects.filter(type=LABEL_TYPE_DEFAULT).order_by('name').only('name').all()
        tarot_labels = Label.objects.filter(type='TAROT').only('name').all()
        label_names = [label.name for label in labels]
        default_type_labels_names = [label.name for label in default_type_labels]
        tarot_label_names = [label.name for label in tarot_labels]
        selected_label_names = self.filter_selected_label_names()
        selected_labels = []
        selected_record_title_fraction = self.request.GET.get('record-title', '')
        if selected_label_names:
            selected_labels = Label.objects.filter(name__in=selected_label_names).all()
        context['labels'] = label_names
        context['default_type_labels'] = default_type_labels_names
        context['selected_labels'] = selected_labels
        context['tarot_labels'] = tarot_label_names
        context['selected_record_title_fraction'] = selected_record_title_fraction
        return context


class RecordDetailView(View):

    def get(self, request, record_id):
        if Record.objects.filter(id=record_id).exists():
            record = Record.objects.get(id=record_id)
            account_user = request.user
            can_edit = record.can_be_edited_by(account_user)
            has_expenses_label = record.labels.filter(name=EXPENSES_LABEL).exists()
            context = {'record': record, 'can_edit': can_edit, 'has_expenses': has_expenses_label}
            return render(request, "records/record_detail.html", context)
        return redirect('records')


class LabelAjaxView(View):

    def get(self, request, label_name):
        label = Label.objects.filter(pk=label_name)
        if label.exists():
            label = label.get()
            response = {"label_name": label.name,
                        "type": label.type}
            if label.type == LABEL_TYPE_TAROT and label.is_tarot_card():
                response["tarot_image_url"] = label.get_tarot_image()
            return JsonResponse(response, status="200", safe=False)
        else:
            return JsonResponse({}, status="200")


class LabelListAjaxView(View):

    def get(self, request, fragment):
        if not fragment or "NULL" == fragment:
            labels = Label.objects.annotate(num_records=Count('records')).order_by('num_records').all()[:100]
        else:
            labels = Label.objects.filter(name__icontains=fragment).order_by('name').all()
        response = {"labels": []}
        for label in labels:
            response['labels'].append({"name": label.name, "type": label.type})
        return JsonResponse(response, status="200", safe=False)


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


class ExpensesPageView(View):

    def get(self, request, record_id):

        record = Record.objects.get(id=record_id)
        if record.labels.filter(name=EXPENSES_LABEL).exists() and record.files.exists():
            expense_file = record.files.filter(file__endswith=".csv")
            if expense_file.exists():
                expenses_file = expense_file.first().file.path
                try:
                    processor = ExpensesProcessor(expenses_file)  # verify the file is valid inside the constructor
                    response = {
                        "title": "temp-title",
                        "record_id": record_id,
                        "page": 1
                    }
                    return render(request, 'records/expenses.html', response)
                except AssertionError as e:
                    logger.info(f"Invalid csv file in record. record_id: {record_id}")
        logger.info(f"Request of expenses page without label {EXPENSES_LABEL} or no valid csv file. record_id: {record_id}")
        return redirect(reverse('record-detail', args=[record_id]))


class ExpensesTableAjax(View):

    def get(self, request, record_id):
        page = self.request.GET.get('page', '')
        # page_size = self.request.GET.get('page_size', '')
        ascending = self.request.GET.get('ascending', '')
        query = self.request.GET.get('filter', '')
        record = Record.objects.get(id=record_id)
        if not page or not page.isdigit() or int(page) < 0:
            page = 1
        else:
            page = int(page)
        ascending = not ascending or ascending.s1.strip().lower() != "false"

        if record.labels.filter(name=EXPENSES_LABEL).exists() and record.files.exists():
            expense_file = record.files.filter(file__endswith=".csv")
            if expense_file.exists():
                expenses_file = expense_file.first().file.path
                try:
                    processor = ExpensesProcessor(expenses_file)
                    data, columns, num_pages, actual_page = processor.query_from_str(query, page=page, ascending=ascending, to_format="json")
                    response = {
                        "title": "temp-title",
                        "columns": columns,
                        "data": data,
                        "record_id": record_id,
                        "num_pages": num_pages,
                        "page": actual_page
                    }
                    return JsonResponse(response, status="200", safe=False)
                except AssertionError as e:
                    logger.info(f"Invalid csv file in record. record_id: {record_id}")
        return JsonResponse({}, status="200")


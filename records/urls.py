from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    # Recorder
    path("", login_required(views.IndexPageView.as_view(), login_url="login"), name="records-index-page"),
    path("add-label", login_required(views.AddLabelView.as_view(), login_url="login"), name="add-label"),
    path("add-record", login_required(views.AddRecordView.as_view(), login_url="login"), name="add-record"),
    path("edit-label", login_required(views.EditLabelView.as_view(), login_url="login"), name="edit-label"),
    path("edit-record/<int:record_id>", login_required(views.EditRecordView.as_view(), login_url="login"), name="edit-record"),
    path("labels", login_required(views.LabelsView.as_view(), login_url="login"), name="labels"),
    path("records", login_required(views.RecordsView.as_view(), login_url="login"), name="records"),
    path("records/<int:record_id>", login_required(views.RecordDetailView.as_view(), login_url="login"), name="record-detail"),
    path("delete-label/<str:label_name>", login_required(views.DeleteLabelView.as_view(), login_url="login"), name="delete-label"),
    path("delete-record/<int:record_id>", login_required(views.DeleteRecordView.as_view(), login_url="login"), name="delete-record"),
    # Expenses
    path("expenses/<int:record_id>", login_required(views.ExpensesPageView.as_view(), login_url="login"), name="expenses"),
    # AJAX
    path("expenses/table/<int:record_id>", login_required(views.ExpensesTableAjax.as_view(), login_url="login"), name="expenses-table-ajax"),
    path("label-info/<str:label_name>", login_required(views.LabelAjaxView.as_view(), login_url="login"), name="label-info-ajax"),
    path("label-list/<str:fragment>", login_required(views.LabelListAjaxView.as_view(), login_url="login"), name="label-list-ajax")
]

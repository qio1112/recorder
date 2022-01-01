from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("calculator", login_required(views.CalculatorView.as_view(), login_url="login"), name="calculator")
]

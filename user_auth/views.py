from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from.forms import CreateUserForm


class SignUpView(View):

    def get(self, request):
        form = CreateUserForm()
        context = {'form': form}
        return render(request, 'user_auth/signup.html', context)

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
        context = {'form': form}
        return render(request, 'user_auth/signup.html', context)


class LoginView(View):

    def get(self, request):
        return render(request, 'user_auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('records-index-page')
        else:
            messages.info(request, "Incorrect Username or Password")
            return redirect('login')


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('login')



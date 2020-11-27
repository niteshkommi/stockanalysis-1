from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from main.decorators import unauthenticated_user


@unauthenticated_user
def index(request):
    return render(request, 'accounts/index.html')


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form':form })


@unauthenticated_user
def login_view(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        raw_password = request.POST.get('password')

        try:
            user = authenticate(
                request, username=username, password=raw_password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.warning(
                    request, "Username or Password is incorrect")
        except (ValueError):
            messages.warning(request, "Please enter a valid username")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
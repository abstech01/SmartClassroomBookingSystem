# accounts/views.py
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import LoginToken
from .utils import generate_token, send_login_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        # Your login logic here
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})
    return render(request, "accounts/login.html")
def request_token_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = generate_token()
            LoginToken.objects.create(user=user, token=token)
            send_login_token(email, token)
            return redirect("verify_token")
        except User.DoesNotExist:
            return render(request, "accounts/request_token.html", {"error": "Email not found."})
    return render(request, "accounts/request_token.html")

def verify_token_view(request):
    if request.method == "POST":
        token = request.POST.get("token")
        try:
            login_token = LoginToken.objects.get(token=token, is_used=False)
            if login_token.is_valid():
                login_token.is_used = True
                login_token.save()
                login(request, login_token.user)
                return redirect("dashboard")
            else:
                return render(request, "accounts/verify_token.html", {"error": "Invalid or expired token."})
        except LoginToken.DoesNotExist:
            return render(request, "accounts/verify_token.html", {"error": "Invalid token."})
    return render(request, "accounts/verify_token.html")

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
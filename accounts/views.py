# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import UserRegistrationForm
from .models import StaffDomain, LoginToken, SystemConfig
from .utils import generate_token, send_login_token

User = get_user_model()


def register_view(request):
    """Passwordless registration. Auto-assign role by email domain."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Auto-assign staff/student based on domain
            email_domain = user.email.split("@")[-1].lower()
            is_staff_domain = StaffDomain.objects.filter(domain__iexact=email_domain).exists()
            if is_staff_domain:
                user.is_staff_user = True
                user.is_student = False
            else:
                user.is_staff_user = False
                user.is_student = True

            user.save()
            messages.success(request, "Account created successfully. Please log in with your email.")
            return redirect("request_token")  # make sure your URL name matches
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def request_token_view(request):
    """Step 1: User enters email; send a 7-char token via Mailjet (or console in dev)."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "accounts/request_token.html")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found. Please register first.")
            return render(request, "accounts/request_token.html")

        token = generate_token()
        LoginToken.objects.create(user=user, token=token)
        send_login_token(email, token)

        messages.success(request, "A login code has been sent to your email.")
        request.session["pending_email"] = email  # store for verify step
        return redirect("verify_token")

    return render(request, "accounts/request_token.html")


def verify_token_view(request):
    """Step 2: User enters token; verify within TTL from newest SystemConfig and login."""
    # Determine TTL (minutes) from latest enabled SystemConfig; default to 2
    cfg = SystemConfig.latest_enabled()
    ttl_minutes = cfg.token_expiry_minutes if cfg else 2

    if request.method == "POST":
        token_input = (request.POST.get("token") or "").strip().upper()
        email = (request.session.get("pending_email") or "").strip().lower()

        if not email:
            messages.error(request, "Your session expired. Please request a new code.")
            return redirect("request_token")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("request_token")

        login_token = (
            LoginToken.objects
            .filter(user=user, token=token_input, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if login_token and login_token.is_valid(ttl_minutes=ttl_minutes):
            login_token.is_used = True
            login_token.save(update_fields=["is_used"])
            login(request, user)
            # cleanup
            request.session.pop("pending_email", None)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid or expired code.")

    return render(request, "accounts/verify_token.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("request_token")  # or 'login' if that's your URL name


@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")

def landing_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("request_token")

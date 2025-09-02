from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_redirect, name="home"),          # 👈 add this
    path("register/", views.register_view, name="register"),
    path("login/", views.request_token_view, name="request_token"),
    path("login/", views.request_token_view, name="login"),
    path("verify/", views.verify_token_view, name="verify_token"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]

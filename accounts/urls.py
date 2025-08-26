from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),         # root shows login
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('request-token/', views.request_token_view, name='request_token'),
    path('verify-token/', views.verify_token_view, name='verify_token')

]

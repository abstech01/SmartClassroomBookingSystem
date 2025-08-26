from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('accounts.urls')),   # accounts handles root now
    path('admin/', admin.site.urls),
]

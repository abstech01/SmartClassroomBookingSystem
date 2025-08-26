from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'campus')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'campus')

# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, StaffDomain, SystemConfig, LoginToken

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff_user", "is_student", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff_user", "is_student", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Roles (app-level)", {"fields": ("is_staff_user", "is_student")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

@admin.register(StaffDomain)
class StaffDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "created_at")
    search_fields = ("domain",)

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ("sender_email", "token_expiry_minutes", "is_enabled", "created_at")
    list_filter = ("is_enabled",)
    readonly_fields = ("created_at",)

@admin.register(LoginToken)
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "is_used")
    search_fields = ("user__email", "token")
    readonly_fields = ("created_at",)

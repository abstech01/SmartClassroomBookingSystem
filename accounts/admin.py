from django.contrib import admin
from .models import SiteConfig, LoginToken

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("token_expiry_minutes", "from_email")

    def has_add_permission(self, request):
        # Prevent creating more than 1 config
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the config
        return False

@admin.register(LoginToken)
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "is_used")
    readonly_fields = ("created_at",)
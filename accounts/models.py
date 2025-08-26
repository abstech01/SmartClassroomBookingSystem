from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    CAMPUS_CHOICES = [
        ('SUVA', 'Suva'),
        ('LAUTOKA', 'Lautoka'),
        ('NADI', 'Nadi'),
        ('LABASA', 'Labasa'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    campus = models.CharField(max_length=20, choices=CAMPUS_CHOICES, default='SUVA')

    def __str__(self):
        return f"{self.user.username}'s profile"

class LoginToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=7)  # 4 letters + 3 digits
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        from .models import SiteConfig
        config = SiteConfig.get_config()
        expiry_minutes = config.token_expiry_minutes
        return (timezone.now() - self.created_at) < timedelta(minutes=expiry_minutes) and not self.is_used


class SiteConfig(models.Model):
    token_expiry_minutes = models.PositiveIntegerField(default=2)
    mailjet_api_key = models.CharField(max_length=255, blank=True, null=True)
    mailjet_api_secret = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.EmailField(default="smartbooking413@gmail.com")

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    @classmethod
    def get_config(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
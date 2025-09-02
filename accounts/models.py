# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        # Superuser may still be passwordless if you want; but usually provide one here
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # remove username entirely
    email = models.EmailField(unique=True)

    # roles (derived at registration from domain rules)
    is_staff_user = models.BooleanField(default=False)  # lecturers/admin role marker
    is_student = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no username

    objects = UserManager()

    def __str__(self):
        return self.email


# ===== domain + config + token =====

class StaffDomain(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.domain

class SystemConfig(models.Model):
    mailjet_api_key = models.CharField(max_length=255, blank=True, null=True)
    mailjet_secret_key = models.CharField(max_length=255, blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True)
    token_expiry_minutes = models.IntegerField(default=2)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Config ({self.created_at:%Y-%m-%d %H:%M})"
    @classmethod
    def latest_enabled(cls):
        return cls.objects.filter(is_enabled=True).order_by("-created_at").first()
    
class LoginToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ use swappable reference
    token = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self, ttl_minutes: int):
        return (not self.is_used) and timezone.now() <= self.created_at + timedelta(minutes=ttl_minutes)

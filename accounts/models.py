from django.db import models
from django.contrib.auth.models import User

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

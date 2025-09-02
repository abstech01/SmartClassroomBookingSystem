from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Campus(models.Model):
    name = models.CharField(max_length=120, unique=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=120)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("campus", "name")
        ordering = ["campus__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.campus.name})"


class RoomPhoto(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="room_photos/")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"Photo for {self.room}"

User = settings.AUTH_USER_MODEL

def times_overlap(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and a_end > b_start

class StudentBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_bookings")
    room = models.ForeignKey("bookings.Room", on_delete=models.CASCADE, related_name="student_bookings")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    purpose = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room", "starts_at", "ends_at"]),
        ]

    def clean(self):
        if self.starts_at >= self.ends_at:
            raise ValidationError("End time must be after start time.")

        # Reject overlap with ANY booking on the same room (students or staff)
        from .models import StaffBooking  # local import to avoid circular
        student_conflicts = StudentBooking.objects.filter(
            room=self.room
        ).exclude(pk=self.pk).filter(
            starts_at__lt=self.ends_at,
            ends_at__gt=self.starts_at,
        ).exists()

        staff_conflicts = StaffBooking.objects.filter(
            room=self.room
        ).exclude(pk=getattr(self, "pk", None)).filter(
            starts_at__lt=self.ends_at,
            ends_at__gt=self.starts_at,
        ).exists()

        if student_conflicts or staff_conflicts:
            raise ValidationError("This room is not available for the selected time.")

    def __str__(self):
        return f"[Student] {self.room} {self.starts_at:%Y-%m-%d %H:%M} → {self.ends_at:%H:%M}"


class StaffBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="staff_bookings")
    room = models.ForeignKey("bookings.Room", on_delete=models.CASCADE, related_name="staff_bookings")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    purpose = models.TextField(blank=True)
    override_comment = models.TextField(blank=True)  # required only if overriding student booking
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room", "starts_at", "ends_at"]),
        ]

    def clean(self):
        if self.starts_at >= self.ends_at:
            raise ValidationError("End time must be after start time.")

        # Staff cannot overlap other staff bookings
        staff_conflict = StaffBooking.objects.filter(
            room=self.room
        ).exclude(pk=self.pk).filter(
            starts_at__lt=self.ends_at,
            ends_at__gt=self.starts_at,
        ).exists()
        if staff_conflict:
            raise ValidationError("You cannot overlap another staff booking.")
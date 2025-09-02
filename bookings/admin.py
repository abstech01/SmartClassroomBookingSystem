from django.contrib import admin
from .models import Campus, Room, RoomPhoto, StaffBooking, StudentBooking

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "address")

class RoomPhotoInline(admin.TabularInline):
    model = RoomPhoto
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "campus", "capacity", "is_active")
    list_filter = ("campus", "is_active")
    search_fields = ("name", "campus__name")
    inlines = [RoomPhotoInline]

@admin.register(RoomPhoto)
class RoomPhotoAdmin(admin.ModelAdmin):
    list_display = ("room", "display_order", "created_at")
    list_filter = ("room__campus",)

@admin.register(StaffBooking)
class StaffBookingAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "starts_at", "ends_at", "created_at")
    list_filter = ("room__campus", "room")
    search_fields = ("user__email", "room__name")

@admin.register(StudentBooking)
class StudentBookingAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "starts_at", "ends_at", "created_at")
    list_filter = ("room__campus", "room")
    search_fields = ("user__email", "room__name")
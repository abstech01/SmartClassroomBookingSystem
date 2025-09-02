# bookings/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from .models import Room, StudentBooking, StaffBooking
from .forms import AvailabilitySearchForm, StudentBookingForm, StaffBookingForm

def room_list(request):
    rooms = Room.objects.select_related("campus").prefetch_related("photos")
    form = AvailabilitySearchForm(request.GET or None)

    availability = {}
    has_query = False
    if form.is_valid():
        has_query = True
        s = form.cleaned_data["starts_at"]
        e = form.cleaned_data["ends_at"]

        for room in rooms:
            # Conflicts for student bookings
            student_conflict = StudentBooking.objects.filter(
                room=room,
                starts_at__lt=e,
                ends_at__gt=s,
            ).exists()

            # Conflicts for staff bookings
            staff_conflict = StaffBooking.objects.filter(
                room=room,
                starts_at__lt=e,
                ends_at__gt=s,
            ).exists()

            # Status logic:
            # - For students, any conflict => unavailable
            # - For staff users, we’ll label specially in template
            availability[room.id] = {
                "student_unavailable": (student_conflict or staff_conflict),
                "staff_unavailable": staff_conflict,  # staff cannot overlap staff
                "student_conflict_only": (student_conflict and not staff_conflict),
            }

    context = {
        "rooms": rooms,
        "form": form,
        "availability": availability,
        "has_query": has_query,
    }
    return render(request, "bookings/room_list.html", context)


def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related("campus").prefetch_related("photos"), pk=pk)
    return render(request, "bookings/room_detail.html", {"room": room})


@login_required
def book_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    is_staff_user = getattr(request.user, "is_staff_user", False)

    # On GET: parse the times from query string; show confirm page
    if request.method == "GET":
        form = AvailabilitySearchForm(request.GET or None)
        if not form.is_valid():
            messages.error(request, "Please search and select a valid start and end time first.")
            return redirect("bookings:room_list")

        s = form.cleaned_data["starts_at"]
        e = form.cleaned_data["ends_at"]

        # Determine if a student booking exists in this slot (for staff override UI)
        student_overlap = StudentBooking.objects.filter(
            room=room, starts_at__lt=e, ends_at__gt=s
        ).exists()

        context = {
            "room": room,
            "starts_at": s,
            "ends_at": e,
            "starts_raw": request.GET.get("starts_at", ""),  # keep original (for hidden inputs/back link)
            "ends_raw": request.GET.get("ends_at", ""),
            "is_staff_user": is_staff_user,
            "must_override": is_staff_user and student_overlap,
        }
        return render(request, "bookings/booking_confirm.html", context)

    # On POST: we only expect hidden start/end + optional override_comment (staff)
    if request.method == "POST":
        starts_raw = request.POST.get("starts_at", "")
        ends_raw = request.POST.get("ends_at", "")
        s = parse_datetime(starts_raw)
        e = parse_datetime(ends_raw)

        if not s or not e or s >= e:
            messages.error(request, "Invalid time range.")
            return redirect("bookings:room_list")

        if is_staff_user:
            # Staff rules:
            # - cannot overlap staff bookings
            staff_conflict = StaffBooking.objects.filter(
                room=room, starts_at__lt=e, ends_at__gt=s
            ).exists()
            if staff_conflict:
                messages.error(request, "You cannot overlap another staff booking.")
                return redirect("bookings:room_detail", pk=room.pk)

            # if overlapping student booking, need override comment
            student_overlap = StudentBooking.objects.filter(
                room=room, starts_at__lt=e, ends_at__gt=s
            ).exists()
            override_comment = (request.POST.get("override_comment") or "").strip()
            if student_overlap and not override_comment:
                messages.error(request, "Override comment is required to override a student booking.")
                # Re-render page with same context
                context = {
                    "room": room,
                    "starts_at": s, "ends_at": e,
                    "starts_raw": starts_raw, "ends_raw": ends_raw,
                    "is_staff_user": is_staff_user,
                    "must_override": True,
                }
                return render(request, "bookings/booking_confirm.html", context)

            # Create staff booking
            StaffBooking.objects.create(
                user=request.user, room=room,
                starts_at=s, ends_at=e,
                purpose="", override_comment=override_comment
            )
            messages.success(request, "Staff booking created.")
            return redirect("bookings:room_detail", pk=room.pk)

        else:
            # Student rules: cannot overlap any booking
            conflict = (
                    StudentBooking.objects.filter(room=room, starts_at__lt=e, ends_at__gt=s).exists() or
                    StaffBooking.objects.filter(room=room, starts_at__lt=e, ends_at__gt=s).exists()
            )
            if conflict:
                messages.error(request, "This room is not available for the selected time.")
                return redirect("bookings:room_detail", pk=room.pk)

            StudentBooking.objects.create(
                user=request.user, room=room,
                starts_at=s, ends_at=e,
                purpose="",
            )
            messages.success(request, "Booking created.")
            return redirect("bookings:room_detail", pk=room.pk)

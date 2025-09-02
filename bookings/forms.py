# bookings/forms.py
from django import forms
from django.utils import timezone
from .models import StudentBooking, StaffBooking

DATETIME_INPUT_KW = {
    "type": "datetime-local",
    "class": "form-control",
}

class AvailabilitySearchForm(forms.Form):
    starts_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs=DATETIME_INPUT_KW))
    ends_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs=DATETIME_INPUT_KW))

    def clean(self):
        data = super().clean()
        s, e = data.get("starts_at"), data.get("ends_at")
        if s and e and s >= e:
            raise forms.ValidationError("End time must be after start time.")
        return data


class StudentBookingForm(forms.ModelForm):
    class Meta:
        model = StudentBooking
        fields = ["starts_at", "ends_at", "purpose"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs=DATETIME_INPUT_KW),
            "ends_at": forms.DateTimeInput(attrs=DATETIME_INPUT_KW),
            "purpose": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class StaffBookingForm(forms.ModelForm):
    class Meta:
        model = StaffBooking
        fields = ["starts_at", "ends_at", "purpose", "override_comment"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs=DATETIME_INPUT_KW),
            "ends_at": forms.DateTimeInput(attrs=DATETIME_INPUT_KW),
            "purpose": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "override_comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Required only if you are overriding a student booking"}),
        }

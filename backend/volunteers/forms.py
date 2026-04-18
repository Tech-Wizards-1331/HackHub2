from django import forms

from .models import VolunteerProfile


class VolunteerProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = []  # No extra fields for volunteers

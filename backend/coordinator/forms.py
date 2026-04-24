from django import forms
from .models import CoordinatorProfile


class CoordinatorProfileForm(forms.ModelForm):
    """Minimal profile form for coordinators (no extra fields required yet)."""

    class Meta:
        model = CoordinatorProfile
        fields = []  # No additional fields to fill — auto-complete on invite accept

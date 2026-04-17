from django import forms

from .models import OrganizerProfile

INPUT_CLASS = (
    'w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2.5 '
    'text-sm text-slate-100 placeholder:text-slate-400 '
    'focus:border-cyan-400 focus:outline-none'
)


class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ['organization_name']
        widgets = {
            'organization_name': forms.TextInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'Your organization or company name'}
            ),
        }

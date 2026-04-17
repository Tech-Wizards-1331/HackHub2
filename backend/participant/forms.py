from django import forms

from .models import ParticipantProfile

INPUT_CLASS = (
    'w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2.5 '
    'text-sm text-slate-100 placeholder:text-slate-400 '
    'focus:border-cyan-400 focus:outline-none'
)


class ParticipantProfileForm(forms.ModelForm):
    class Meta:
        model = ParticipantProfile
        fields = ['github_link', 'college', 'experience']
        widgets = {
            'github_link': forms.URLInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'https://github.com/username'}
            ),
            'college': forms.TextInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'Your college or university'}
            ),
            'experience': forms.Select(
                attrs={'class': INPUT_CLASS},
            ),
        }

    def __init__(self, *args, hide_github=False, **kwargs):
        super().__init__(*args, **kwargs)
        if hide_github:
            self.fields.pop('github_link', None)

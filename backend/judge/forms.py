from django import forms

from .models import JudgeProfile

INPUT_CLASS = (
    'w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2.5 '
    'text-sm text-slate-100 placeholder:text-slate-400 '
    'focus:border-cyan-400 focus:outline-none'
)


class JudgeProfileForm(forms.ModelForm):
    class Meta:
        model = JudgeProfile
        fields = ['expertise', 'linkedin', 'years_of_experience']
        widgets = {
            'expertise': forms.TextInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. AI/ML, Web Development, Cybersecurity'}
            ),
            'linkedin': forms.URLInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'https://linkedin.com/in/yourprofile'}
            ),
            'years_of_experience': forms.NumberInput(
                attrs={'class': INPUT_CLASS, 'placeholder': 'Years of experience', 'min': '0'}
            ),
        }

from django import forms
from .models import Hackathon, ProblemStatement


class DateTimeLocalInput(forms.DateTimeInput):
    """
    A DateTimeInput widget that always renders the value in the
    HTML5 `datetime-local` format (YYYY-MM-DDTHH:MM) so that
    re-renders after failed submissions don't produce blank fields.
    """
    input_type = 'datetime-local'
    format = '%Y-%m-%dT%H:%M'

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, format='%Y-%m-%dT%H:%M')


class HackathonForm(forms.ModelForm):
    class Meta:
        model = Hackathon
        fields = [
            'name',
            'description',
            'start_date',
            'end_date',
            'registration_deadline',
            'status',
            'min_team_size',
            'max_team_size',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'syntra-input',
                'placeholder': 'Enter hackathon name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'syntra-input',
                'rows': 4,
                'placeholder': 'Describe your hackathon...',
            }),
            'start_date': DateTimeLocalInput(attrs={'class': 'syntra-input'}),
            'end_date': DateTimeLocalInput(attrs={'class': 'syntra-input'}),
            'registration_deadline': DateTimeLocalInput(attrs={'class': 'syntra-input'}),
            'status': forms.Select(attrs={
                'class': 'syntra-input',
            }),
            'min_team_size': forms.NumberInput(attrs={
                'class': 'syntra-input',
                'min': 1,
            }),
            'max_team_size': forms.NumberInput(attrs={
                'class': 'syntra-input',
                'min': 1,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        reg_deadline = cleaned_data.get('registration_deadline')
        min_size = cleaned_data.get('min_team_size')
        max_size = cleaned_data.get('max_team_size')

        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', 'End date must be after the start date.')

        if start_date and reg_deadline and reg_deadline >= start_date:
            self.add_error(
                'registration_deadline',
                'Registration deadline must be before the hackathon start date.',
            )

        if min_size and max_size and max_size < min_size:
            self.add_error('max_team_size', 'Max team size cannot be less than min team size.')

        return cleaned_data


class ProblemStatementForm(forms.ModelForm):
    class Meta:
        model = ProblemStatement
        fields = ['title', 'description', 'pdf_file', 'max_teams_allowed', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'syntra-input',
                'placeholder': 'Problem statement title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'syntra-input',
                'rows': 4,
                'placeholder': 'Describe the problem...',
            }),
            'pdf_file': forms.ClearableFileInput(attrs={
                'class': 'syntra-input',
            }),
            'max_teams_allowed': forms.NumberInput(attrs={
                'class': 'syntra-input',
                'min': 1,
                'placeholder': 'e.g. 5',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }

    def clean_pdf_file(self):
        f = self.cleaned_data.get('pdf_file')
        if f and hasattr(f, 'size') and f.size > 10 * 1024 * 1024:  # 10 MB limit
            raise forms.ValidationError('PDF file must be smaller than 10 MB.')
        return f

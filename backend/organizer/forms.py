from django import forms
from .models import Hackathon, ProblemStatement


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
            'start_date': forms.DateTimeInput(attrs={
                'class': 'syntra-input',
                'type': 'datetime-local',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'syntra-input',
                'type': 'datetime-local',
            }),
            'registration_deadline': forms.DateTimeInput(attrs={
                'class': 'syntra-input',
                'type': 'datetime-local',
            }),
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

from django import forms
from .models import Team, TeamMember

class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email', 'college', 'semester', 'degree', 'skills']
        widgets = {
            'skills': forms.CheckboxSelectMultiple()
        }

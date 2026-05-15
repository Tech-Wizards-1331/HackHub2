from django.urls import path
from .views import HackathonListView, HackathonRegisterWizardView, ParticipantHackathonHubView

urlpatterns = [
    path('hackathons/', HackathonListView.as_view(), name='hackathon-list'),
    path('hackathons/<int:pk>/register/', HackathonRegisterWizardView.as_view(), name='hackathon-register'),
    path('hackathons/<int:pk>/hub/', ParticipantHackathonHubView.as_view(), name='participant-hackathon-hub'),
]

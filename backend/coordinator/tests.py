from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from organizer.models import Hackathon, HackathonCoordinator, OrganizerProfile
from .models import CoordinatorProfile

User = get_user_model()

class CoordinatorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create organizer
        self.organizer_user = User.objects.create_user(email='org@test.com', password='pw', role=User.Role.ORGANIZER)
        self.organizer_profile = OrganizerProfile.objects.create(user=self.organizer_user)
        
        # Create hackathon
        self.hackathon = Hackathon.objects.create(
            name="Test Hackathon",
            description="Test",
            start_date="2026-05-01T00:00:00Z",
            end_date="2026-05-02T00:00:00Z",
            registration_start="2026-04-01T00:00:00Z",
            registration_deadline="2026-04-30T00:00:00Z",
            organizer=self.organizer_profile
        )
        
        # Create coordinator
        self.coord_user = User.objects.create_user(email='coord@test.com', password='pw', role=User.Role.COORDINATOR)
        self.coord_profile = CoordinatorProfile.objects.create(user=self.coord_user)
        
        # Assign coordinator
        self.assignment = HackathonCoordinator.objects.create(
            user=self.coord_user,
            hackathon=self.hackathon,
            responsibilities=['problem_statements', 'analytics']
        )
        
    def test_dashboard_access_allowed_for_coordinator(self):
        self.client.force_authenticate(user=self.coord_user)
        url = reverse('coordinator-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        import json
        print("\n--- Dashboard API Output ---")
        print(json.dumps(data, indent=2))
        print("----------------------------\n")
        self.assertIn('hackathons', data)
        self.assertEqual(len(data['hackathons']), 1)
        self.assertEqual(data['hackathons'][0]['name'], "Test Hackathon")
        self.assertIn('problem_statements', data['hackathons'][0]['responsibilities'])
        
    def test_dashboard_access_denied_for_organizer(self):
        self.client.force_authenticate(user=self.organizer_user)
        url = reverse('coordinator-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

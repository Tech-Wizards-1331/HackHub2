from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from unittest.mock import patch
from .models import Hackathon, HackathonCoordinator, OrganizerProfile
from .tasks import send_coordinator_invite_email

User = get_user_model()

class OrganizerCoordinatorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create organizer
        self.org_user = User.objects.create_user(email='org@test.com', password='pw', role=User.Role.ORGANIZER)
        self.org_profile = OrganizerProfile.objects.create(user=self.org_user)
        
        # Create hackathon
        self.hackathon = Hackathon.objects.create(
            name="Org Hackathon",
            description="Test",
            start_date="2026-05-01T00:00:00Z",
            end_date="2026-05-02T00:00:00Z",
            registration_start="2026-04-01T00:00:00Z",
            registration_deadline="2026-04-30T00:00:00Z",
            organizer=self.org_profile
        )
        
        # Create another user to be coordinator
        self.coord_user = User.objects.create_user(email='newcoord@test.com', password='pw')
        
    def test_list_coordinators(self):
        # Assign first
        HackathonCoordinator.objects.create(
            user=self.coord_user,
            hackathon=self.hackathon,
            responsibilities=['analytics']
        )
        
        self.client.force_authenticate(user=self.org_user)
        url = reverse('hackathon-list-coordinators', kwargs={'pk': self.hackathon.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_email'], 'newcoord@test.com')
        self.assertIn('analytics', data[0]['responsibilities'])

    def test_unassign_coordinator(self):
        # Assign first
        HackathonCoordinator.objects.create(
            user=self.coord_user,
            hackathon=self.hackathon
        )
        
        self.client.force_authenticate(user=self.org_user)
        url = reverse('hackathon-unassign-coordinator', kwargs={'pk': self.hackathon.id})
        response = self.client.post(url, {'email': 'newcoord@test.com'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(HackathonCoordinator.objects.filter(hackathon=self.hackathon, user=self.coord_user).exists())

    def test_unassign_nonexistent_coordinator(self):
        self.client.force_authenticate(user=self.org_user)
        url = reverse('hackathon-unassign-coordinator', kwargs={'pk': self.hackathon.id})
        response = self.client.post(url, {'email': 'fake@test.com'}, format='json')
        
    @patch('organizer.tasks.send_coordinator_invite_email.delay')
    def test_assign_new_user_creates_invite(self, mock_send_email_delay):
        self.client.force_authenticate(user=self.org_user)
        url = reverse('hackathon-assign-coordinator', kwargs={'pk': self.hackathon.id})
        
        # 'unknown@test.com' doesn't exist yet
        response = self.client.post(url, {
            'email': 'unknown@test.com',
            'responsibilities': ['teams']
        }, format='json')
        
        # Should be created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('successfully created and invited', response.json()['message'])
        
        # Check user was created
        new_user = User.objects.get(email='unknown@test.com')
        self.assertEqual(new_user.role, User.Role.COORDINATOR)
        self.assertFalse(new_user.has_usable_password())
        
        # Check celery task was queued
        self.assertTrue(mock_send_email_delay.called)
        
        # Check assignment was created
        self.assertTrue(HackathonCoordinator.objects.filter(hackathon=self.hackathon, user=new_user).exists())

    def test_celery_task_sends_email(self):
        # Execute the task synchronously for testing
        send_coordinator_invite_email.apply(kwargs={
            'email': 'test@example.com',
            'hackathon_name': 'Global Hack',
            'invite_url': 'http://localhost:8000/invite/123'
        })
        
        # Verify an email was added to the outbox
        self.assertEqual(len(mail.outbox), 1)
        
        sent_msg = mail.outbox[0]
        self.assertEqual(sent_msg.subject, 'You have been invited as a Coordinator for Global Hack')
        self.assertEqual(sent_msg.to, ['test@example.com'])
        self.assertIn('http://localhost:8000/invite/123', sent_msg.body)
        self.assertIn('Global Hack', sent_msg.body)
        
        # Verify HTML alternative exists
        self.assertTrue(hasattr(sent_msg, 'alternatives'))
        html_content = sent_msg.alternatives[0][0]
        self.assertIn('http://localhost:8000/invite/123', html_content)
        self.assertIn('Global Hack', html_content)

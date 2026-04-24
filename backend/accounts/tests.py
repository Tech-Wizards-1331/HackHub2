from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_accept_invite_sets_password(self):
        # Create an inactive/invited user
        user = User.objects.create(email='invited@test.com', role=User.Role.COORDINATOR)
        user.set_unusable_password()
        user.save()
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        url = reverse('accept_invite', kwargs={'uidb64': uid, 'token': token})
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/accept_invite.html')
        
        # Test POST request to set password
        response = self.client.post(url, {
            'full_name': 'Invited Coordinator',
            'password1': 'NewStrongPassword123!',
            'password2': 'NewStrongPassword123!'
        })
        
        # Should redirect to complete_profile (or dashboard depending on logic)
        self.assertRedirects(response, reverse('complete_profile'), fetch_redirect_response=False)
        
        # Verify user state
        user.refresh_from_db()
        self.assertTrue(user.has_usable_password())
        self.assertEqual(user.full_name, 'Invited Coordinator')
        
        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_invalid_token_rejected(self):
        user = User.objects.create(email='invited@test.com', role=User.Role.COORDINATOR)
        user.set_unusable_password()
        user.save()
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = 'invalid-token-123'
        
        url = reverse('accept_invite', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        
        # Should redirect to login with error
        self.assertRedirects(response, reverse('login'))
        
        # User shouldn't be changed
        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())

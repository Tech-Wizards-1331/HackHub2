from django.conf import settings
from django.db import models

class CoordinatorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coordinator_profile',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'CoordinatorProfile({self.user.email})'

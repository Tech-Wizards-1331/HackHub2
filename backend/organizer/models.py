from django.conf import settings
from django.db import models


class OrganizerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organizer_profile',
    )
    organization_name = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f'OrganizerProfile({self.user.email})'

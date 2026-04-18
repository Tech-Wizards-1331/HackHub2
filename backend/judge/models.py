from django.conf import settings
from django.db import models


class JudgeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='judge_profile',
    )
    expertise = models.CharField(max_length=255, blank=True, default='')
    linkedin = models.URLField(max_length=300, blank=True, default='')
    years_of_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'JudgeProfile({self.user.email})'

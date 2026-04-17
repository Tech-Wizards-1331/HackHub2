from django.conf import settings
from django.db import models


class Skill(models.Model):
    """Reusable skill tag (e.g. Python, React, Machine Learning)."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ParticipantProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participant_profile',
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='participants')
    github_link = models.URLField(max_length=300, blank=True, default='')
    college = models.CharField(max_length=255, blank=True, default='')
    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        blank=True,
        default='',
    )

    def __str__(self):
        return f'ParticipantProfile({self.user.email})'

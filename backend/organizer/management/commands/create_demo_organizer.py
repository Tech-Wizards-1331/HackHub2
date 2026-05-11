from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from organizer.models import OrganizerProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a demo organizer account'

    def handle(self, *args, **kwargs):
        email = 'org@gmail.com'
        password = 'Admin@123'
        
        user, created = User.objects.get_or_create(email=email)
        user.set_password(password)
        user.role = 'organizer'
        user.is_profile_complete = True
        user.save()
        
        OrganizerProfile.objects.get_or_create(
            user=user,
            defaults={'organization_name': 'Demo Organization'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created demo organizer "{email}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated demo organizer "{email}"'))

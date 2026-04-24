from rest_framework import permissions
from django.contrib.auth import get_user_model
from organizer.models import HackathonCoordinator

User = get_user_model()

class IsCoordinator(permissions.BasePermission):
    """Layer 1: Allows access only to users with the COORDINATOR role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.COORDINATOR)
        
class CoordinatorPermissionMixin:
    """
    Mixin for ViewSets to handle Layer 2 and Layer 3 permissions.
    Requires `required_responsibility` attribute to be set on the ViewSet (Layer 3).
    """
    def get_coordinator_assignments(self):
        """Returns HackathonCoordinator queryset for the current user."""
        return HackathonCoordinator.objects.filter(user=self.request.user).select_related('hackathon').prefetch_related('hackathon__problem_statements')
        
    def get_accessible_hackathons(self):
        """Layer 2 & 3: Returns hackathons the user is assigned to WITH the required responsibility."""
        assignments = self.get_coordinator_assignments()
        
        # Layer 3 check
        required_resp = getattr(self, 'required_responsibility', None)
        if required_resp:
            # Filter assignments that contain the required responsibility
            assignments = [a for a in assignments if required_resp in a.responsibilities]
            
        hackathon_ids = [a.hackathon_id for a in assignments]
        from organizer.models import Hackathon
        return Hackathon.objects.filter(id__in=hackathon_ids).prefetch_related('problem_statements')

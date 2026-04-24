"""
Dynamic responsibility-based permissions for the organizer app.

These permission classes allow both Organizers and Coordinators to share
the same API endpoints, with access gated by the coordinator's assigned
responsibilities on a per-hackathon basis.
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model

from .models import HackathonCoordinator

User = get_user_model()


def has_responsibility(user, hackathon, responsibility):
    """Check if a user has a specific responsibility for a hackathon.

    Organizers always return True (full access).
    Coordinators are checked against HackathonCoordinator.responsibilities.
    """
    if user.role == User.Role.ORGANIZER:
        return True
    return HackathonCoordinator.objects.filter(
        user=user,
        hackathon=hackathon,
        responsibilities__contains=[responsibility],
    ).exists()


class IsOrganizerOrHasResponsibility(permissions.BasePermission):
    """Base permission class for responsibility-scoped access.

    Subclass this and set `responsibility_required` to the specific
    Responsibility enum value.
    """
    responsibility_required = None  # Override in subclass

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.ORGANIZER:
            return True
        if request.user.role == User.Role.COORDINATOR:
            # Let has_object_permission or get_queryset handle the specifics
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ORGANIZER:
            return True
        # Resolve the hackathon from the object
        if hasattr(obj, 'hackathon'):
            hackathon = obj.hackathon
        else:
            hackathon = obj  # The object IS a Hackathon
        return has_responsibility(
            request.user, hackathon, self.responsibility_required
        )


class CanManageProblemStatements(IsOrganizerOrHasResponsibility):
    """Allows organizers + coordinators with PROBLEM_STATEMENTS responsibility."""
    responsibility_required = HackathonCoordinator.Responsibility.PROBLEM_STATEMENTS


class CanManageTeams(IsOrganizerOrHasResponsibility):
    """Allows organizers + coordinators with TEAM_MANAGEMENT responsibility."""
    responsibility_required = HackathonCoordinator.Responsibility.TEAM_MANAGEMENT


class CanViewAnalytics(IsOrganizerOrHasResponsibility):
    """Allows organizers + coordinators with ANALYTICS responsibility."""
    responsibility_required = HackathonCoordinator.Responsibility.ANALYTICS


class IsOrganizer(permissions.BasePermission):
    """Allows access only to users with the ORGANIZER role."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ORGANIZER
        )


class IsOrganizerOrReadOnlyCoordinator(permissions.BasePermission):
    """Organizers get full access; Coordinators get read-only (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.ORGANIZER:
            return True
        if request.user.role == User.Role.COORDINATOR:
            return request.method in permissions.SAFE_METHODS
        return False

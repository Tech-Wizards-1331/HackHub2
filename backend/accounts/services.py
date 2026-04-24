"""
accounts/services.py — Business logic layer for authentication and profile management.

All business rules live here. Views should be thin HTTP glue calling these services.
This follows the Service Layer pattern (Django best practice for non-trivial apps).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm

from allauth.socialaccount.models import SocialAccount

from .models import User
from participant.models import ParticipantProfile, Skill
from participant.forms import ParticipantProfileForm
from organizer.models import OrganizerProfile
from organizer.forms import OrganizerProfileForm
from judge.models import JudgeProfile
from judge.forms import JudgeProfileForm
from volunteers.models import VolunteerProfile
from volunteers.forms import VolunteerProfileForm
from coordinator.models import CoordinatorProfile
from coordinator.forms import CoordinatorProfileForm

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Role ↔ Profile Registry
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RoleProfileConfig:
    """Immutable configuration binding a role to its profile model, form, and URL."""
    model: type[Model]
    form: type[ModelForm]
    related_name: str
    dashboard_url: str


# Single source of truth for all role → profile mappings.
# To add a new role, add ONE entry here. Nothing else needs changing.
ROLE_REGISTRY: dict[str, RoleProfileConfig] = {
    User.Role.PARTICIPANT: RoleProfileConfig(
        model=ParticipantProfile,
        form=ParticipantProfileForm,
        related_name='participant_profile',
        dashboard_url='/participant/dashboard',
    ),
    User.Role.ORGANIZER: RoleProfileConfig(
        model=OrganizerProfile,
        form=OrganizerProfileForm,
        related_name='organizer_profile',
        dashboard_url='/organizer/dashboard',
    ),
    User.Role.JUDGE: RoleProfileConfig(
        model=JudgeProfile,
        form=JudgeProfileForm,
        related_name='judge_profile',
        dashboard_url='/judge/dashboard',
    ),
    User.Role.VOLUNTEER: RoleProfileConfig(
        model=VolunteerProfile,
        form=VolunteerProfileForm,
        related_name='volunteer_profile',
        dashboard_url='/volunteers/dashboard',
    ),
    User.Role.COORDINATOR: RoleProfileConfig(
        model=CoordinatorProfile,
        form=CoordinatorProfileForm,
        related_name='coordinator_profile',
        dashboard_url='/coordinator/',
    ),
}

# Super admin has a dashboard but no profile model.
SUPER_ADMIN_DASHBOARD_URL = '/super_admin/dashboard'


def get_role_config(role: Optional[str]) -> Optional[RoleProfileConfig]:
    """Look up profile config for a role. Returns None for unknown/admin roles."""
    return ROLE_REGISTRY.get(role)


def get_dashboard_url(user: User) -> Optional[str]:
    """Resolve the dashboard URL for a user based on their role."""
    config = get_role_config(user.role)
    if config:
        return config.dashboard_url
    if user.is_superuser:
        return SUPER_ADMIN_DASHBOARD_URL
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Profile Lifecycle
# ──────────────────────────────────────────────────────────────────────────────

def cleanup_stale_profiles(user: User, *, keep_role: Optional[str] = None) -> int:
    """Delete all role-specific profiles for `user` except `keep_role`.

    Returns the total number of deleted rows.
    """
    deleted_total = 0
    for role, config in ROLE_REGISTRY.items():
        if role != keep_role:
            count, _ = config.model.objects.filter(user=user).delete()
            if count:
                logger.info(
                    'Deleted %s profile for user %s (role switch to %s)',
                    role, user.pk, keep_role,
                )
            deleted_total += count
    return deleted_total


@transaction.atomic
def switch_user_role(user: User, new_role: str) -> bool:
    """Atomically switch a user's role, cleaning up any stale profile data.

    Returns True if the role actually changed, False if it stayed the same.
    """
    old_role = user.role
    role_changed = old_role != new_role

    if role_changed and old_role:
        cleanup_stale_profiles(user, keep_role=new_role)

    user.role = new_role
    user.is_profile_complete = False
    user.save(update_fields=['role', 'is_profile_complete', 'updated_at'])

    logger.info('User %s role: %s → %s', user.pk, old_role, new_role)
    return role_changed


@transaction.atomic
def save_profile(user: User, profile_form: ModelForm, *, skills_csv: str = '') -> None:
    """Save a role-specific profile and mark the user's profile as complete.

    Handles M2M skill processing for participants and GitHub auto-linking.
    """
    profile_obj = profile_form.save(commit=False)
    profile_obj.user = user
    profile_obj.save()

    # Handle Participant-specific M2M skills
    if user.role == User.Role.PARTICIPANT and isinstance(profile_obj, ParticipantProfile):
        _process_participant_skills(profile_obj, skills_csv)
        _auto_fill_github(user, profile_obj)

    # Save any remaining M2M relationships declared on the form
    profile_form.save_m2m()

    # Mark profile as complete
    user.is_profile_complete = True
    user.save(update_fields=['is_profile_complete', 'updated_at'])

    logger.info('Profile completed for user %s (role=%s)', user.pk, user.role)


def _process_participant_skills(profile: ParticipantProfile, skills_csv: str) -> None:
    """Parse comma-separated skill names, get-or-create Skill objects, set on profile."""
    skill_names = [s.strip() for s in skills_csv.split(',') if s.strip()]
    if not skill_names:
        profile.skills.clear()
        return

    skill_objects = []
    for name in skill_names:
        # Case-insensitive dedup: find existing or create with original casing
        skill = Skill.objects.filter(name__iexact=name).first()
        if not skill:
            skill = Skill.objects.create(name=name)
        skill_objects.append(skill)

    profile.skills.set(skill_objects)


def _auto_fill_github(user: User, profile: ParticipantProfile) -> None:
    """If user signed up via GitHub and github_link is empty, auto-fill it."""
    if profile.github_link:
        return

    github_url = get_github_profile_url(user)
    if github_url:
        profile.github_link = github_url
        profile.save(update_fields=['github_link'])
        logger.info('Auto-filled GitHub link for user %s', user.pk)


# ──────────────────────────────────────────────────────────────────────────────
# Social Account Helpers
# ──────────────────────────────────────────────────────────────────────────────

def has_social_account(user: User, provider: str) -> bool:
    """Check if the user has a connected social account for the given provider."""
    return SocialAccount.objects.filter(user=user, provider=provider).exists()


def get_github_profile_url(user: User) -> str:
    """Extract the GitHub html_url from the social account extra_data."""
    try:
        sa = SocialAccount.objects.get(user=user, provider='github')
        return (sa.extra_data or {}).get('html_url', '')
    except SocialAccount.DoesNotExist:
        return ''


# ──────────────────────────────────────────────────────────────────────────────
# Navigation Helpers
# ──────────────────────────────────────────────────────────────────────────────

def resolve_post_login_destination(user: User) -> str:
    """Determine where to send a user after login/signup.

    Priority: no role → select_role, incomplete profile → complete_profile, else → dashboard.
    """
    if not user.role:
        return 'select_role'
    if not user.is_profile_complete:
        return 'complete_profile'
    return get_dashboard_url(user) or 'select_role'

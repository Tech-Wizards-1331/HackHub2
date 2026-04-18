"""
accounts/views.py — Thin view layer.

Views handle HTTP concerns only: reading request data, calling services,
setting messages, and returning responses. No business logic lives here.
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialApp

from .forms import LoginForm, ProfileCompletionForm, RoleSelectionForm, SignUpForm
from .models import User
from .services import (
    get_dashboard_url,
    get_role_config,
    has_social_account,
    resolve_post_login_destination,
    save_profile,
    switch_user_role,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Internal Helpers (HTTP-layer only)
# ──────────────────────────────────────────────────────────────────────────────

def _safe_next_url(request: HttpRequest) -> str | None:
    """Validate and return a safe ?next= redirect URL, or None."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if not next_url:
        return None
    if url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def _redirect_by_state(user: User) -> HttpResponse:
    """Redirect a user to the right place based on their current state."""
    destination = resolve_post_login_destination(user)

    # destination is either a URL name or a full path
    if destination.startswith('/'):
        return redirect(destination)
    return redirect(destination)


# ──────────────────────────────────────────────────────────────────────────────
# Auth Views
# ──────────────────────────────────────────────────────────────────────────────

@never_cache
def signup_view(request: HttpRequest) -> HttpResponse:
    """Handle new user registration."""
    if request.user.is_authenticated:
        return _redirect_by_state(request.user)

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.role = None
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account created successfully. Please select your role to continue.')
        return redirect('select_role')

    return render(request, 'accounts/signup.html', {'form': form})


@never_cache
def login_view(request: HttpRequest) -> HttpResponse:
    """Handle email/password login with optional ?next= redirect."""
    if request.user.is_authenticated:
        safe_next = _safe_next_url(request)
        if safe_next:
            return redirect(safe_next)
        return _redirect_by_state(request.user)

    form = LoginForm(request.POST or None)
    safe_next = _safe_next_url(request)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].strip().lower()
        password = form.cleaned_data['password']
        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, 'Invalid credentials.')
        else:
            login(request, user)
            if safe_next:
                return redirect(safe_next)
            return _redirect_by_state(user)

    return render(request, 'accounts/login.html', {'form': form, 'next': safe_next or ''})


@require_POST
@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """Log the user out and redirect to login.

    Returns JSON for fetch() calls (Accept: application/json),
    otherwise redirects to the login page.
    """
    logout(request)

    # fetch()-based logout → return JSON so JS can handle redirect
    if 'application/json' in request.headers.get('Accept', ''):
        resp = JsonResponse({'ok': True})
        resp.delete_cookie('sessionid')
        return resp

    # Regular form POST fallback
    response = redirect('/accounts/login/')
    response.delete_cookie('sessionid')
    return response


# ──────────────────────────────────────────────────────────────────────────────
# Onboarding Views
# ──────────────────────────────────────────────────────────────────────────────

@never_cache
@login_required
def select_role_view(request: HttpRequest) -> HttpResponse:
    """Let the user pick (or change) their role before profile completion."""
    user = request.user

    # Auto-assign super_admin role for superusers
    if user.is_superuser and not user.role:
        switch_user_role(user, User.Role.SUPER_ADMIN)
        return _redirect_by_state(user)

    # Lock role selection once profile IS complete
    if user.role and user.is_profile_complete:
        return _redirect_by_state(user)

    form = RoleSelectionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        selected_role = form.cleaned_data['role']
        switch_user_role(user, selected_role)
        messages.success(request, 'Role selected successfully.')
        return redirect('complete_profile')

    return render(request, 'accounts/select_role.html', {'form': form})


@never_cache
@login_required
def complete_profile_view(request: HttpRequest) -> HttpResponse:
    """Render and process the role-specific profile completion form.

    The @never_cache decorator sets Cache-Control, Pragma, and Expires headers
    to prevent browsers from serving a stale cached version.
    """
    # Always re-fetch from DB to guarantee fresh role data
    user = User.objects.get(pk=request.user.pk)

    # Guard: superusers skip profile completion
    if user.is_superuser and not user.is_profile_complete:
        user.is_profile_complete = True
        user.save(update_fields=['is_profile_complete', 'updated_at'])
        return _redirect_by_state(user)

    # Guard: already complete → dashboard
    if user.is_profile_complete:
        return _redirect_by_state(user)

    # Guard: no role selected yet
    if not user.role:
        return redirect('select_role')

    # Resolve the role's profile configuration
    config = get_role_config(user.role)
    if not config:
        # Unmapped role (shouldn't happen) — mark complete and move on
        user.is_profile_complete = True
        user.save(update_fields=['is_profile_complete', 'updated_at'])
        return _redirect_by_state(user)

    # Get or create the profile instance for the current role
    profile, _ = config.model.objects.get_or_create(user=user)

    # Detect GitHub social link for conditional form rendering
    user_has_github = has_social_account(user, 'github')
    is_participant = user.role == User.Role.PARTICIPANT

    # Build the role-specific form
    form_kwargs: dict = {'instance': profile}
    if is_participant:
        form_kwargs['hide_github'] = user_has_github

    # Base user form (full_name)
    user_form = ProfileCompletionForm(request.POST or None, instance=user)

    if request.method == 'POST':
        profile_form = config.form(request.POST, **form_kwargs)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            save_profile(
                user,
                profile_form,
                skills_csv=request.POST.get('skills', ''),
            )
            messages.success(request, 'Profile completed successfully!')
            return _redirect_by_state(user)
    else:
        profile_form = config.form(**form_kwargs)

    context = {
        'form': user_form,
        'profile_form': profile_form,
        'user_role': user.role,
        'has_github': user_has_github,
        'is_participant': is_participant,
    }
    return render(request, 'accounts/complete_profile.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# Social Auth Entry Points
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def social_login_redirect(request: HttpRequest) -> HttpResponse:
    """Post-social-login routing — sends user to role selection or dashboard."""
    return _redirect_by_state(request.user)


def _social_provider_configured(request: HttpRequest, provider: str) -> bool:
    """Check if a social provider has valid credentials configured."""
    try:
        get_adapter(request).get_app(request, provider=provider)
    except SocialApp.DoesNotExist:
        return False
    except MultipleObjectsReturned:
        return False
    return True


def google_login_entry(request: HttpRequest) -> HttpResponse:
    """Legacy entry point for Google OAuth — redirects to allauth's canonical URL."""
    if not _social_provider_configured(request, 'google'):
        messages.error(
            request,
            'Google login is not configured. Set GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET '
            'or add a Google SocialApp in /admin/.',
        )
        return redirect('login')

    query_string = request.META.get('QUERY_STRING')
    target = reverse('google_login')
    if query_string:
        target = f'{target}?{query_string}'
    return redirect(target)


def github_login_entry(request: HttpRequest) -> HttpResponse:
    """Legacy entry point for GitHub OAuth — redirects to allauth's canonical URL."""
    if not _social_provider_configured(request, 'github'):
        messages.error(
            request,
            'GitHub login is not configured. Set GITHUB_CLIENT_ID/GITHUB_CLIENT_SECRET '
            'or add a GitHub SocialApp in /admin/.',
        )
        return redirect('login')

    query_string = request.META.get('QUERY_STRING')
    target = reverse('github_login')
    if query_string:
        target = f'{target}?{query_string}'
    return redirect(target)

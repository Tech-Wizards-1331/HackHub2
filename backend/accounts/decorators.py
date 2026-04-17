"""
accounts/decorators.py — Access control decorators.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.cache import never_cache


def role_required(*allowed_roles):
    """Restrict view access to users with one of the given roles.

    Also applies @never_cache so that after logout, pressing the browser
    Back button will NOT show a cached version of the protected page.
    Superusers bypass role checks.
    """
    def decorator(view_func):
        @never_cache
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = getattr(request.user, 'role', None)
            if request.user.is_superuser or user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('You are not allowed to access this page.')

        return _wrapped_view

    return decorator

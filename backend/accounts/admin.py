from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for the User model.
    Superusers can create accounts with any role (participant / organizer / super_admin)
    and edit roles of existing users.
    """

    # ── List view ──────────────────────────────────────────────────────────
    list_display   = ('email', 'full_name', 'role', 'is_profile_complete', 'is_active', 'is_staff', 'created_at')
    list_filter    = ('role', 'is_active', 'is_staff', 'is_profile_complete')
    list_editable  = ('role',)          # Edit role directly from the list – no need to open each user
    search_fields  = ('email', 'full_name')
    ordering       = ('-created_at',)

    # ── Detail / edit view ─────────────────────────────────────────────────
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('full_name',)
        }),
        ('Role & Status', {
            'fields': ('role', 'is_profile_complete', 'is_active', 'is_staff', 'is_superuser'),
            'description': 'Set the role to <b>participant</b> or <b>organizer</b>.'
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # ── Create new user view ───────────────────────────────────────────────
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'full_name', 'role', 'password1', 'password2', 'is_active'),
            'description': 'Choose <b>organizer</b> or <b>participant</b> in the Role field below.',
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
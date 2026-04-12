# Integrations

## Authentication Providers
The project is integrated with `django-allauth` for social authentication.

| Service | Status | Description |
|---------|--------|-------------|
| **Google OAuth** | Configured | Uses environment variables for client ID and secret. |
| **GitHub OAuth** | Configured | Uses environment variables for client ID and secret. |

## External APIs
- **None Currently Active**: The configuration for `social_django` is present but commented out in `settings.py` and `urls.py` in favor of `allauth`.

## Internal Services
- **Custom User Flow**: A middleware (`accounts.middleware.UserFlowMiddleware`) exists to manage user redirection based on profile completion and role.
- **Role Map**: `ROLE_DASHBOARD_MAP` in `accounts/views.py` maps user roles to specific dashboard paths.

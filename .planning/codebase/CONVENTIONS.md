# Conventions

## Code Style
- **Django Standard**: Follows standard Django conventions (PEP 8 for Python).
- **Template Tagging**: Extensive use of `{% load static %}` and `{% url %}` tags in HTML templates.

## Architecture Patterns
- **User Roles**: Roles are defined as `TextChoices` in the `User` model.
- **Onboarding Flow**: Enforced by `UserFlowMiddleware`. Users are redirected until `is_profile_complete` is `True`.
- **Form Handling**: Use of Django `ModelForm` for signup and profile completion.

## Frontend Conventions
- **Tailwind CSS**: Utility classes are used directly in templates.
- **Modern Typography**: Inter and Orbitron fonts used for a tech-heavy aesthetic.
- **Interactivity**: Particle canvases and cursor glows (Vanilla JS) are integrated into the landing page.

## File Organization
- Apps are modularized by user role.
- Templates are often placed both in `templates/` (global) and app-specific `templates/` dirs.

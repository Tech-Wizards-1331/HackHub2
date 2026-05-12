# Structure

## Directory Layout
- `backend/`: Root directory for the Django project.
  - `syntra/`: Project configuration, core routing, WSGI/ASGI entry points.
  - `accounts/`: Application for user management, profiles, and auth.
  - `organizer/`: Application containing hackathon management features.
  - `participant/`: Application containing participant dashboard features.
  - `media/`: Development directory for user-uploaded files (e.g., PDFs).
  - `staticfiles/`: Target directory for collected static files for production.
  - `manage.py`: Django command-line utility.
  - `requirements.txt`: Python package dependencies.
  - `build.sh`: Build script used by Render for deployment.
- `frontend/`: Root directory for all frontend assets.
  - `templates/`: Global Django templates.
  - `static/`: Global static files (CSS, JS, images).
- `/`: Workspace root containing configuration and deployment files (e.g., `render.yaml`, `.env`).

## Naming Conventions
- Django applications follow standard lower-case naming based on the domain boundary (e.g., `organizer`, `participant`).
- Environment variables are standard uppercase (e.g., `DATABASE_URL`, `SOCIAL_AUTH_BASE_URL`).

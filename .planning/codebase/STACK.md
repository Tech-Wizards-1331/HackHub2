# Stack

## Backend
- **Framework:** Django 6.0.3 (Python 3.12.3)
- **API:** Django REST Framework (DRF) 3.16.1
- **Database:** PostgreSQL (production via Supabase), SQLite (local dev)
- **Authentication:** `django-allauth` for OAuth, `djangorestframework-simplejwt` for API tokens.
- **Background Tasks:** `django-celery-beat` (installed, but Celery config currently commented/removed in settings).

## Frontend
- **Templating:** Django Templates (`frontend/templates/`)
- **Static Assets:** Vanilla CSS/JS (`frontend/static/`)
- **Static File Serving:** WhiteNoise 6.12.0

## Infrastructure
- **Hosting:** Render.com (`render.yaml`)
- **Environment Management:** `python-dotenv` for local `.env`

## Rationale
The stack uses robust, proven Python technologies to quickly bootstrap the hackathon management platform, leveraging Render for zero-downtime deployment and Supabase for a managed PostgreSQL instance.

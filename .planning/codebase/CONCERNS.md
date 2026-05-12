# Concerns

## Technical Debt & Issues
- **Authentication Hybridization:** The application uses a mix of session authentication (for server-rendered templates) and JWT (for DRF APIs). This hybrid approach can cause edge cases in client-side state management.
- **Background Tasks:** `django-celery-beat` is installed, but `settings.py` indicates that the Celery configuration has been removed ("only auth remains"). If asynchronous jobs are needed, Celery configuration must be fully restored and properly integrated.
- **Frontend Coupling:** The frontend heavily couples Django templates with static files located outside the Django root (`frontend/`). As the project scales, migrating to a decoupled React/Next.js frontend may become challenging.

## Deployment Fragility
- Using SQLite locally while deploying to PostgreSQL in production can mask database-specific bugs (e.g., JSONField handling or exact string matching differences).

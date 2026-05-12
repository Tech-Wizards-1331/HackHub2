# Conventions

## Code Style
- **Python:** Standard PEP-8 conventions via Django standard practices.
- **Settings:** Environment variables manage all secure and environment-specific configurations via `python-dotenv` locally and cloud provider native env vars in production.

## Application Boundaries
- The system is built around Domain-Driven Design concepts inside Django apps.
- `organizer` handles the event orchestration logic.
- `participant` handles user consumption and registration.
- Shared models (like the User model) are kept inside `accounts`.

## Security
- Strict deployment checks in `settings.py` for SSL redirection (`SECURE_SSL_REDIRECT`), secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`), and HSTS.
- WhiteNoise is configured for static file compression and caching.

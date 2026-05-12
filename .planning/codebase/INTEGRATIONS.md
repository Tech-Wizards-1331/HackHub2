# Integrations

## Databases
- **Supabase PostgreSQL:** Primary database for production, configured via `DATABASE_URL`.

## Authentication Providers
- **Google OAuth:** Integrated via `django-allauth`. Configured using `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
- **GitHub OAuth:** Integrated via `django-allauth`. Configured using `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`.

## External Services
- **Render.com:** Cloud provider. Deployment blueprint is defined in `render.yaml`.
- **SMTP Provider:** Standard SMTP configuration for email delivery (`EMAIL_HOST`, `EMAIL_PORT`, etc.). Local fallback to console.

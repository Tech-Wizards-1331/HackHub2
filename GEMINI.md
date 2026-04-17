<!-- GSD:project-start source:PROJECT.md -->
## Project

**Syntra**

Syntra is a hackathon management platform that handles the full lifecycle of hackathon events — from creation and team formation through submissions, judging, and logistics (attendance, food distribution). Built with Django, it serves organizers, participants, judges, and administrators through a modular, domain-driven backend.

**Core Value:** A complete, production-ready Django model layer that accurately represents the full hackathon management domain — users, hackathons, teams, submissions, judging, notifications, and operations — with proper relationships, constraints, and scalable patterns.

### Constraints

- **Schema fidelity**: Do NOT change the business logic or relationships from the provided schema
- **Tech stack**: Django 6.0.3, Python
- **Auth model**: Must use existing custom User model pattern (email-based, AbstractUser)
- **Role architecture**: Admin = global role on User model; participant/judge/organizer = per-hackathon via UserRole
- **App modularity**: Models grouped by domain, not by user role
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Language & Runtime
- **Python** — Primary backend language
- **Django 6.0.3** — Web framework, latest major version
- **HTML/CSS/JS** — Frontend templates (server-side rendered)
## Framework
- **Django 6.0.3** — Full-stack web framework
## Dependencies (`backend/requirements.txt`)
| Package | Version | Purpose |
|---------|---------|---------|
| Django | 6.0.3 | Web framework |
| django-allauth | 65.13.0 | Social auth (Google, GitHub OAuth) |
| python-dotenv | 1.2.1 | Environment variable management |
| djangorestframework | 3.16.1 | REST API framework |
| djangorestframework-simplejwt | 5.5.1 | JWT authentication for APIs |
| requests | 2.32.5 | HTTP client |
| PyJWT | 2.12.1 | JWT token handling |
| cryptography | 46.0.5 | Cryptographic operations |
## Database
- **SQLite3** — `backend/db.sqlite3` (development only)
- No PostgreSQL or production DB configured yet
## Configuration
- **Settings module:** `backend/syntra/settings.py` (primary), `backend/project/settings.py` (extends syntra settings)
- **Manage.py:** Points to `project.settings` (which imports from `syntra.settings`)
- **Environment:** `.env` file at project root, loaded via `python-dotenv`
- **Auth model:** `AUTH_USER_MODEL = 'accounts.User'`
- **Time zone:** `Asia/Kolkata`
- **Debug mode:** `True` (hardcoded)
- **Secret key:** Hardcoded insecure key (needs rotation for production)
## Frontend
- **Server-side templates** in `frontend/templates/`
- **Static files** in `frontend/static/css/` and `frontend/static/js/`
- **Tailwind CSS** — Used in form widget classes (e.g., `w-full rounded-xl border...`)
- No JavaScript framework — plain HTML templates with Django template language
## Dual Settings Architecture
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Code Style
- **Python:** Loosely follows PEP 8
## Naming
- **Models:** PascalCase (`User`, `CustomUserManager`)
- **Views:** snake_case functions (`login_view`, `signup_view`, `select_role_view`)
- **API Views:** PascalCase classes (`RegisterAPIView`, `LoginAPIView`, `MeAPIView`)
- **URLs:** Kebab-case paths (`/select-role/`, `/complete-profile/`, `/social-redirect/`)
- **URL names:** Snake_case (`select_role`, `complete_profile`, `social_login_redirect`)
- **Form classes:** PascalCase (`SignUpForm`, `LoginForm`, `ProfileCompletionForm`)
- **Constants:** UPPER_CASE (`ROLE_DASHBOARD_MAP`, `INPUT_CLASS`, `ROLE_CHOICES`)
- **Prefixes:** API files use `api_` prefix (`api_views.py`, `api_serializers.py`, `api_urls.py`)
## Patterns
### Role-based Access Control
### Dashboard Routing
### Form Styling
### Social Auth Entry Points
## Error Handling
- **Form validation:** Django form `clean()` methods with `forms.ValidationError`
- **API validation:** DRF `serializers.ValidationError` with field-level errors
- **Auth errors:** `messages.error()` for template views, DRF exception for API
- **Access control:** `HttpResponseForbidden` via `@role_required()` decorator
- **Social auth errors:** Check if provider configured, redirect with message if not
## Import Organization
## Configuration Patterns
- **Env vars** loaded via `python-dotenv` from `.env` at project root
- **OAuth keys** read via `os.getenv()` with empty string defaults
- **Settings inheritance** via `from syntra.settings import *` in `project/settings.py`
## Comments
- Minimal inline comments
- Some Hindi comments exist (e.g., `# ✅ Superuser ne ignore karo` in middleware)
- Emoji-prefixed comments in middleware for visual scanning (`# ✅`, `# 🔹`)
- Legacy code comments preserved (e.g., `# Uncomment once social-auth-app-django is installed`)
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern
## Layers
### 1. URL Routing Layer
- `backend/syntra/urls.py` — Primary URL config (allauth + template views)
- `backend/project/urls.py` — Extended URL config (adds `api` app routes)
- Each role app has its own `urls.py` with a single dashboard route
### 2. View Layer (Mixed)
- **Template views:** `backend/accounts/views.py` — Full auth flow (login, signup, role selection, profile completion, social auth)
- **API views:** `backend/accounts/api_views.py` — DRF-based register, login, me endpoints
- **Role dashboards:** Each role app has one `home()` view rendering a template
### 3. Model Layer
- **Only one real model:** `backend/accounts/models.py` → `User` (custom, email-based)
- All other apps have empty `models.py` files (`# Create your models here.`)
- No hackathon, team, submission, or judging models exist yet
### 4. Middleware Layer
- `backend/accounts/middleware.py` → `UserFlowMiddleware`
### 5. Serialization Layer
- `backend/accounts/api_serializers.py` — Register, Login serializers
- `backend/api/serializers.py` — Re-exports from accounts (proxy)
## Authentication Architecture
### Dual Auth Strategy
### User Flow (Template-based)
```
```
### User Flow (API-based)
```
```
## Role System
- **Global role** on `User.role` — Single role per user
- Available roles: `participant`, `organizer`, `judge`, `volunteer`, `super_admin`
- **No per-hackathon roles** — Current architecture assigns one global role
- Role-based access via `@role_required()` decorator in `backend/accounts/decorators.py`
- Dashboard routing via `ROLE_DASHBOARD_MAP` dict in `backend/accounts/views.py`
## Data Flow
```
```
```
```
## Entry Points
| Entry Point | File | Purpose |
|-------------|------|---------|
| `/` | `backend/core/views.py` → `home()` | Landing page |
| `/accounts/login/` | `backend/accounts/views.py` → `login_view()` | User login |
| `/accounts/signup/` | `backend/accounts/views.py` → `signup_view()` | User registration |
| `/api/auth/register/` | `backend/accounts/api_views.py` → `RegisterAPIView` | API registration |
| `/api/auth/login/` | `backend/accounts/api_views.py` → `LoginAPIView` | API login |
| `/admin/` | Django admin | Admin panel |
| `/{role}/dashboard` | Each role app's `views.py` | Role-specific dashboard |
## Key Abstractions
- `CustomUserManager` — Email-based user creation
- `SyntraSocialAccountAdapter` — Social auth preference + user merging
- `UserFlowMiddleware` — Enforces signup completion flow
- `role_required()` — Role-based access control decorator
## Current Limitations
- **No domain models** — No hackathon, team, submission, or judging models
- **Role-per-user** — Cannot be a participant in one hackathon and judge in another
- **Empty apps** — participant, organizer, judge, volunteers, super_admin have no models
- **No API beyond auth** — Only auth endpoints exist in REST API
- **SQLite-only** — No production database support
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.agent/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

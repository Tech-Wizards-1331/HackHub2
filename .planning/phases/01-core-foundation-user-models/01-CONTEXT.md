# Context: Core Foundation & User Models

**Phase:** 1
**Status:** Decided
**Last Updated:** 2026-04-17

## Decisions

### 1. Identity & Profile Split
- **User Model:** Custom User (AbstractUser) will be stripped of nearly all profile-related fields. It remains minimal for Auth: email (unique PK), password, `is_active`, `is_staff`, `is_superuser`.
- **UserProfile Model:** A `UserProfile` model will be created as a `OneToOneField` with `User`.
- **Field Migration:** Fields like `full_name` will be moved from the `User` model to the `UserProfile` model. This keeps the Auth layer isolated from the domain-specific profile data.

### 2. Base Models (Core)
- **Location:** A new `core` app will hold the reusable architectural models.
- **TimestampedModel:** Abstract base class providing `created_at` (auto_now_add) and `updated_at` (auto_now).
- **SoftDeleteModel:** Abstract base class providing a `deleted_at` (null=True, blank=True) timestamp.
- **Logic:** Soft deletion will be implemented via manager filtering (default logic is `objects` filters out non-null `deleted_at`).

### 3. Identity Manager
- **CustomUserManager:** A manager for the `User` model will be implemented to support email-based registration (replacing username logic in `create_user` and `create_superuser`).

### 4. Auth Flow Middleware
- **Transition:** `UserFlowMiddleware` will be updated to check for the existence of a `UserProfile` instance instead of the legacy `is_profile_complete` boolean on the `User` model.
- **Cleanup:** Old role-selection logic (mapping to the global role Enum) will be removed from the middleware's logic to make room for the future hackathon-specific role system.

## Specifics

- **Primary Identity:** Email is the `USERNAME_FIELD`.
- **Soft Delete:** Simple manager-level filtering. No complex cascade handling for now (Phase 1).
- **Storage:** Metadata fields previously stored in session (organisation, phone, etc.) will eventually map to the `UserProfile` in a future phase, but we'll ensure the `UserProfile` can accommodate them now.

## Canonical Refs

- `backend/accounts/models.py` (Existing User model)
- `backend/accounts/middleware.py` (Auth flow logic to be refactored)
- `backend/syntra/settings.py` (AUTH_USER_MODEL config)

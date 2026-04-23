# Phase 3: Coordinator Login and Signup - Summary

**Completed:** 2026-04-23
**Status:** Verified & Complete

## What Was Built

The "Coordinator Login and Signup" phase implemented the backend logic and views required for onboarding new coordinators. Since coordinators cannot sign up organically, the flow relies on invite links dispatched by Sub-Admins.

### Key Deliverables

1. **Invite Dispatch Logic (`assign_coordinator`):**
   - Modified the `assign_coordinator` endpoint in the `organizer` app.
   - When a Sub-Admin assigns an email that doesn't exist, the system creates a shell `User` with `User.Role.COORDINATOR` and `has_usable_password() == False`.
   - Generates a secure token using Django's `PasswordResetTokenGenerator` and emails an expiring link to the user.

2. **Invite Redemption Flow (`accept_invite_view`):**
   - Built a secure endpoint (`/accounts/invite/accept/<uidb64>/<token>/`) to process invite links.
   - Decodes the user ID and verifies the token's validity and expiration.
   - If valid, renders an HTML form for the user to set their full name and password.

3. **User Interface (`accept_invite.html`):**
   - Created the template for the invite redemption page.
   - Maintained visual consistency with the existing auth UI (gradient buttons, dark-mode styling, error states).

4. **Nyquist Testing:**
   - Added `test_assign_new_user_creates_invite` to `backend/organizer/tests.py`.
   - Added `test_accept_invite_sets_password` and `test_invalid_token_rejected` to `backend/accounts/tests.py`.
   - All tests pass, validating that unknown emails receive invites and proper validation prevents token reuse.

## Future Recommendations
- Currently, when an invite is accepted, the system redirects to the `complete_profile` flow. Because a `CoordinatorProfile` model wasn't mapped yet in `services.py`, the system simply marks the profile as complete and redirects. This is acceptable for now, but a dedicated `CoordinatorProfile` should be implemented in future phases to capture more specific details.
- Move email dispatches to background tasks (Celery) in future iterations to improve API response times for `assign_coordinator`.

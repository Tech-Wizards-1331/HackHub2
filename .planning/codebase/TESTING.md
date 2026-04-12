# Testing

## Current Strategy
The codebase currently relies on manual verification.

## Automated Tests
- **Status**: Minimal coverage.
- **Files**: App-specific `tests.py` files exist but are currently placeholders (~63 bytes).
- **Tooling**: Uses standard `django.test`.

## Verification Priorities
1. **Authentication**: Sign-up and login logic must be verified.
2. **Onboarding Flow**: Middleware redirection logic is critical.
3. **Role-Based Access**: Access to dashboards (Judge, Organizer, etc.) needs validation.

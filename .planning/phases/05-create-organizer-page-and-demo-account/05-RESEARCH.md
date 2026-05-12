# Phase 5 Research: Organizer Page and Demo Account

## Objective
Research the technical approach to implement the organizer dashboard page using Django templates and create a management command to provision the `org@gmail.com` demo account.

## Technical Approach

### 1. Management Command
- **File Location:** `backend/organizer/management/commands/create_demo_organizer.py`
- **Logic:** Use `BaseCommand`. Fetch the custom `User` model using `get_user_model()`. Use `get_or_create` for `email="org@gmail.com"`. Set the password to `Admin@123` via `user.set_password()`, set `role='organizer'`, `is_profile_complete=True`. Save the user. Use `get_or_create` on `OrganizerProfile` with `organization_name="Demo Organization"`. 
- **Idempotency:** Ensures that rerunning the script won't crash and will reset the password.

### 2. Django View and Template
- **View (`backend/organizer/views.py`):**
  - Create `OrganizerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView)`.
  - `test_func`: Ensures `request.user.role == 'organizer'`.
  - `get_context_data`: Fetch hackathons where `organizer=self.request.user.organizer_profile`.
- **URL Routing (`backend/organizer/urls.py`):**
  - Note: Previously we looked at `api_urls.py`, we need to see if `urls.py` exists or create it for template views. We also need to mount it in the main `backend/syntra/urls.py`.
- **Template (`backend/organizer/templates/organizer/dashboard.html`):**
  - Standard HTML displaying `request.user.organizer_profile.organization_name`.
  - A loop iterating through `hackathons` and displaying their names and status.

## Dependencies & Considerations
- `LoginRequiredMixin` ensures unauthenticated users are redirected to login.
- `UserPassesTestMixin` prevents Participants or Admins from accessing the organizer dashboard.
- The `organizer` app might not have a `templates` directory or `urls.py` yet since it was purely an API. We'll need to create them.

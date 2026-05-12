---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/management/commands/create_demo_organizer.py
  - backend/organizer/views.py
  - backend/organizer/urls.py
  - backend/organizer/templates/organizer/dashboard.html
  - backend/syntra/urls.py
autonomous: true
---

# Phase 5: Create Organizer Page and Demo Account

<must_haves>
- A Django management command to reliably provision the `org@gmail.com` demo account.
- A functional Django TemplateView that acts as the organizer dashboard.
- The dashboard is accessible only to authenticated users with the `organizer` role.
- The dashboard displays the organizer's profile name and a list of their hackathons.
</must_haves>

<threat_model>
- High: Unauthorized users accessing the organizer dashboard. Mitigated by `LoginRequiredMixin` and `UserPassesTestMixin`.
- High: Hardcoded passwords in source code. Accepted risk because this is explicitly a local demo/testing seed command and not used for production user creation.
</threat_model>

<task>
<read_first>
- backend/accounts/models.py
- backend/organizer/models.py
</read_first>
<action>
Create the demo account management command.
1. Create directories `backend/organizer/management/` and `backend/organizer/management/commands/`. Add `__init__.py` files to both to ensure they are treated as Python packages.
2. Create `backend/organizer/management/commands/create_demo_organizer.py`.
3. Implement `Command(BaseCommand)`:
   - Use `get_user_model()` to get the custom User.
   - Try to get or create a user with email `org@gmail.com`.
   - Set password to `Admin@123` via `user.set_password()`.
   - Set `role='organizer'` and `is_profile_complete=True`.
   - Save the user.
   - Use `OrganizerProfile.objects.get_or_create(user=user, defaults={'organization_name': 'Demo Organization'})`.
   - Output success message using `self.stdout.write`.
</action>
<acceptance_criteria>
- `backend/organizer/management/commands/create_demo_organizer.py` exists and is a valid Django management command.
- It creates or updates the `org@gmail.com` user with the correct role and password.
- It creates an associated `OrganizerProfile`.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/models.py
</read_first>
<action>
Create the organizer dashboard view.
1. Create `backend/organizer/views.py` (if it doesn't exist).
2. Import `TemplateView`, `LoginRequiredMixin`, `UserPassesTestMixin`, and `Hackathon` model.
3. Create `OrganizerDashboardView`:
   - `template_name = 'organizer/dashboard.html'`
   - `def test_func(self): return getattr(self.request.user, 'role', None) == 'organizer'`
   - `def get_context_data(self, **kwargs):` fetch hackathons linked to `self.request.user.organizer_profile` and add them to context.
</action>
<acceptance_criteria>
- `backend/organizer/views.py` contains `OrganizerDashboardView`.
- The view restricts access to users with the `organizer` role.
- The view passes the user's hackathons to the template context.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/views.py
</read_first>
<action>
Create the dashboard HTML template.
1. Create directories `backend/organizer/templates/` and `backend/organizer/templates/organizer/`.
2. Create `backend/organizer/templates/organizer/dashboard.html`.
3. Add basic HTML structure:
   - A `<head>` with a title.
   - A `<body>` with a `<h1>` greeting the organization (`{{ request.user.organizer_profile.organization_name }}`).
   - An `<ul>` listing the hackathons.
   - Loop over `{{ hackathons }}` and display their `name` and `status`.
   - If empty, display "No hackathons found."
</action>
<acceptance_criteria>
- `dashboard.html` exists and is valid Django template syntax.
- Displays organization name and loops over hackathons.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/urls.py
- backend/syntra/urls.py
</read_first>
<action>
Register URLs for the new dashboard.
1. Create or update `backend/organizer/urls.py` (this is distinct from `api_urls.py`).
   - Add `path('dashboard/', OrganizerDashboardView.as_view(), name='organizer-dashboard')`.
2. Update `backend/syntra/urls.py` to include the new `organizer.urls`:
   - Add `path('organizer/', include('organizer.urls'))` to `urlpatterns`.
</action>
<acceptance_criteria>
- `backend/organizer/urls.py` correctly mounts `OrganizerDashboardView`.
- `backend/syntra/urls.py` includes `organizer.urls`.
</acceptance_criteria>
</task>

<verification_criteria>
- `python manage.py create_demo_organizer` executes successfully and prints the success message.
- `python manage.py check` reports no syntax or URL configuration issues.
- The server starts without errors.
</verification_criteria>

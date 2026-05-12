---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/forms.py
  - backend/organizer/views.py
  - backend/organizer/urls.py
  - backend/organizer/templates/organizer/create_hackathon.html
  - backend/organizer/templates/organizer/dashboard.html
autonomous: true
---

# Phase 6: Organizer Create Hackathon

<must_haves>
- A Django ModelForm (`HackathonForm`) with essential fields only.
- A `CreateHackathonView` that auto-assigns the organizer and restricts access to the `organizer` role.
- A styled HTML template for the creation form.
- A "Create Hackathon" button on the existing dashboard.
- Redirect to dashboard with success message after creation.
</must_haves>

<threat_model>
- High: Non-organizer users creating hackathons. Mitigated by `LoginRequiredMixin` + `UserPassesTestMixin`.
- Medium: Missing organizer profile causing crash on form save. Mitigated by checking `hasattr(user, 'organizer_profile')` before save.
</threat_model>

<task>
<read_first>
- backend/organizer/models.py
</read_first>
<action>
Create the HackathonForm ModelForm.
1. Create `backend/organizer/forms.py`.
2. Import `forms` from Django and `Hackathon` from models.
3. Create `HackathonForm(forms.ModelForm)`:
   - `Meta.model = Hackathon`
   - `Meta.fields = ['name', 'description', 'start_date', 'end_date', 'registration_deadline', 'min_team_size', 'max_team_size']`
   - Use `DateTimeInput` widgets with `type='datetime-local'` for all three date fields.
</action>
<acceptance_criteria>
- `backend/organizer/forms.py` exists with `HackathonForm`.
- Form includes exactly the 7 specified fields.
- Date fields use HTML5 datetime-local input widgets.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/views.py
- backend/organizer/forms.py
</read_first>
<action>
Add CreateHackathonView to views.py.
1. Import `CreateView`, `reverse_lazy`, `messages`, and `HackathonForm`.
2. Create `CreateHackathonView(LoginRequiredMixin, UserPassesTestMixin, CreateView)`:
   - `model = Hackathon`
   - `form_class = HackathonForm`
   - `template_name = 'organizer/create_hackathon.html'`
   - `success_url = reverse_lazy('organizer-dashboard')`
   - `test_func`: return `self.request.user.role == 'organizer'`
   - `form_valid`: Set `form.instance.organizer = self.request.user.organizer_profile`, add success message via `messages.success()`, then call `super().form_valid(form)`.
</action>
<acceptance_criteria>
- `CreateHackathonView` exists in `views.py`.
- Access restricted to organizer role.
- Organizer profile auto-assigned on save.
- Success message displayed after creation.
</acceptance_criteria>
</task>

<task>
<action>
Create the create_hackathon.html template.
1. Create `backend/organizer/templates/organizer/create_hackathon.html`.
2. Use the same styling as `dashboard.html` (Segoe UI font, container, card style).
3. Include a `<form method="post">` with `{% csrf_token %}`.
4. Render each form field with a label and input.
5. Display form errors using `{{ form.errors }}` and `{{ field.errors }}`.
6. Add a "Create Hackathon" submit button and a "Cancel" link back to dashboard.
</action>
<acceptance_criteria>
- Template exists and renders the form correctly.
- CSRF token included.
- Form errors displayed.
- Visual style matches the dashboard.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/urls.py
- backend/organizer/templates/organizer/dashboard.html
</read_first>
<action>
Register URL and update dashboard.
1. In `backend/organizer/urls.py`, add `path('create-hackathon/', CreateHackathonView.as_view(), name='organizer-create-hackathon')`.
2. In `backend/organizer/templates/organizer/dashboard.html`, add a styled "Create Hackathon" button/link that points to `{% url 'organizer-create-hackathon' %}`. Place it in the header area next to the title. Also add a `{% if messages %}` block to display success messages.
</action>
<acceptance_criteria>
- URL `/organizer/create-hackathon/` resolves correctly.
- Dashboard has a visible "Create Hackathon" button.
- Success messages are displayed on the dashboard after redirect.
</acceptance_criteria>
</task>

<verification_criteria>
- `python manage.py check` passes with no errors.
- Navigating to `/organizer/create-hackathon/` while logged in as organizer shows the form.
- Submitting the form creates a Hackathon and redirects to dashboard.
- The new hackathon appears in the dashboard list.
</verification_criteria>

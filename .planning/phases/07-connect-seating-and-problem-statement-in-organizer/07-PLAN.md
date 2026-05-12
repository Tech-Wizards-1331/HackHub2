---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/forms.py
  - backend/organizer/views.py
  - backend/organizer/urls.py
  - backend/organizer/templates/organizer/dashboard.html
  - backend/organizer/templates/organizer/hackathon_detail.html
  - backend/organizer/templates/organizer/add_problem_statement.html
autonomous: true
---

# Phase 7: Connect Seating & Problem Statement Management in Organizer

<must_haves>
- Hackathon Detail page at `/organizer/hackathon/<id>/` showing read-only hackathon info.
- Problem Statement section: list existing, add new, delete existing.
- Seating Allocation section: JSON textarea for room config, "Run Allocation" button, results table, CSV export link.
- Dashboard hackathon names are clickable links to the detail page.
- Only the owning organizer can access their hackathon detail page.
</must_haves>

<threat_model>
- High: Non-owner accessing another organizer's hackathon. Mitigated by ownership check in every view.
- Medium: Invalid JSON in room_configuration textarea. Mitigated by try/except with user-friendly error message.
</threat_model>

<task>
<read_first>
- backend/organizer/forms.py
- backend/organizer/models.py
</read_first>
<action>
Add ProblemStatementForm and RoomConfigForm to forms.py.
1. Create `ProblemStatementForm(forms.ModelForm)`:
   - `Meta.model = ProblemStatement`
   - `Meta.fields = ['title', 'description', 'pdf_file', 'max_teams_allowed', 'is_active']`
   - Apply `form-input` CSS class to all widgets.
2. Create `RoomConfigForm(forms.Form)`:
   - `room_configuration = forms.CharField(widget=forms.Textarea)` with placeholder showing example JSON format.
</action>
<acceptance_criteria>
- Both forms exist in `forms.py`.
- ProblemStatementForm covers all user-facing fields.
- RoomConfigForm has a single textarea field.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/views.py
- backend/organizer/api_views.py
- backend/organizer/services/seating.py
</read_first>
<action>
Add views for hackathon detail, problem statement CRUD, and seating allocation.

1. `HackathonDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView)`:
   - `model = Hackathon`, `template_name = 'organizer/hackathon_detail.html'`
   - `test_func`: check user role is organizer AND hackathon belongs to user's organizer_profile.
   - `get_context_data`: add `problem_statements` (hackathon.problem_statements.all()), `room_config_form` (pre-filled if room_configuration exists), and `seating_allocation` from the hackathon.

2. `AddProblemStatementView(LoginRequiredMixin, UserPassesTestMixin, CreateView)`:
   - Uses `ProblemStatementForm`, template `organizer/add_problem_statement.html`.
   - `form_valid`: set `form.instance.hackathon` from URL kwarg, verify ownership.
   - `success_url`: redirect back to hackathon detail page.

3. `DeleteProblemStatementView(LoginRequiredMixin, UserPassesTestMixin, DeleteView)`:
   - No template needed — use POST-only with `get_success_url` redirecting to hackathon detail.
   - `test_func`: verify ownership.

4. `RunSeatingAllocationView(LoginRequiredMixin, UserPassesTestMixin, View)`:
   - POST-only. Accepts `room_configuration` JSON from form.
   - Parses JSON (with try/except for invalid JSON), saves to hackathon.room_configuration.
   - Calls `get_teams_for_allocation` and `allocate` from `services.seating`.
   - Saves result to hackathon.seating_allocation.
   - Redirects back to hackathon detail with success/error message.
</action>
<acceptance_criteria>
- All four views exist and are properly access-controlled.
- Problem statement CRUD works through the UI.
- Seating allocation runs the algorithm and stores results.
- Invalid JSON shows an error message instead of crashing.
</acceptance_criteria>
</task>

<task>
<action>
Create hackathon_detail.html template.

Layout:
1. **Header**: Hackathon name, dates, status (read-only).
2. **Problem Statements section**:
   - Table listing: title, max_teams_allowed, is_active, delete button (POST form).
   - "Add Problem Statement" link/button.
3. **Seating Allocation section**:
   - Form with `room_configuration` JSON textarea + "Run Allocation" button.
   - If `seating_allocation` exists: display a summary table from `room_view` data.
   - "Export CSV" link pointing to existing `/api/organizer/hackathons/<id>/seating-export/`.
4. **Back to Dashboard** link.

Style: Match existing dashboard/create_hackathon templates (Segoe UI, container card, same color scheme).
</action>
<acceptance_criteria>
- Template renders hackathon info, problem statements, and seating allocation.
- All forms include CSRF tokens.
- Delete uses POST method.
- CSV export link works.
</acceptance_criteria>
</task>

<task>
<action>
Create add_problem_statement.html template.

Simple form page matching existing styling:
- Fields: title, description, pdf_file, max_teams_allowed, is_active.
- Submit button + Cancel link back to hackathon detail.
- Form errors displayed per-field.
</action>
<acceptance_criteria>
- Template renders the form with all fields.
- Cancel links back to the correct hackathon detail page.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/urls.py
- backend/organizer/templates/organizer/dashboard.html
</read_first>
<action>
Register all new URLs and update the dashboard.

1. Add to `urls.py`:
   - `path('hackathon/<int:pk>/', HackathonDetailView.as_view(), name='organizer-hackathon-detail')`
   - `path('hackathon/<int:hackathon_id>/add-problem-statement/', AddProblemStatementView.as_view(), name='organizer-add-problem-statement')`
   - `path('hackathon/<int:hackathon_id>/delete-problem-statement/<int:pk>/', DeleteProblemStatementView.as_view(), name='organizer-delete-problem-statement')`
   - `path('hackathon/<int:hackathon_id>/run-seating/', RunSeatingAllocationView.as_view(), name='organizer-run-seating')`

2. Update `dashboard.html`:
   - Wrap each hackathon name in an `<a>` tag linking to `{% url 'organizer-hackathon-detail' hackathon.pk %}`.
</action>
<acceptance_criteria>
- All URLs resolve correctly.
- Dashboard hackathon names are clickable.
</acceptance_criteria>
</task>

<verification_criteria>
- `python manage.py check` passes with no errors.
- Navigating to `/organizer/hackathon/<id>/` shows the detail page.
- Adding a problem statement through the form works and redirects back.
- Deleting a problem statement removes it and redirects back.
- Submitting room config JSON runs the allocation and shows results.
- CSV export link downloads the file.
</verification_criteria>

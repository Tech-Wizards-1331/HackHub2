---
wave: 1
depends_on: [Phase 8]
files_modified:
  - backend/participant/models.py
  - backend/participant/urls.py
  - backend/participant/views.py
  - backend/participant/forms.py
  - frontend/templates/participant/hackathon_list.html
  - frontend/templates/participant/hackathon_register.html
autonomous: true
---

# Phase 9: Participant Join Registration (Open Hackathon)

## 1. Database Model Updates

<task>
<read_first>
- backend/participant/models.py
</read_first>
<action>
Modify `Team` model in `backend/participant/models.py`:
- Add `is_registered = models.BooleanField(default=False)`

Modify `TeamMember` model in `backend/participant/models.py`:
- Add a custom `clean` method to enforce email uniqueness per hackathon. If `TeamMember.objects.filter(email=self.email, team__hackathon=self.team.hackathon).exclude(pk=self.pk).exists()` is True, raise ValidationError("This email is already registered for this hackathon.").

Create and apply migrations:
- Run `python manage.py makemigrations participant`
- Run `python manage.py migrate participant`
</action>
<acceptance_criteria>
- `backend/participant/models.py` contains `is_registered = models.BooleanField(default=False)` in `Team`.
- `backend/participant/models.py` contains `def clean(self):` in `TeamMember`.
- Migration file exists in `backend/participant/migrations/`.
</acceptance_criteria>
</task>

## 2. Participant Forms & Views

<task>
<read_first>
- backend/participant/models.py
- backend/organizer/models.py
</read_first>
<action>
Create `backend/participant/forms.py` (if it does not exist) and define:
- `TeamRegistrationForm`: ModelForm for `Team` covering `name`.
- `TeamMemberForm`: ModelForm for `TeamMember` covering `name`, `email`, `college`, `semester`, `degree`, `skills`. Make `college`, `semester`, `degree`, `skills` effectively required when completing the final registration (so the wizard view will validate them at the end, even if draft saves are allowed).

Modify `backend/participant/views.py`:
- Create `HackathonListView` (ListView): queries `Hackathon.objects.filter(status='registration_open')`, renders `participant/hackathon_list.html`.
- Create `HackathonRegisterWizardView` (View):
  - Handles GET/POST with state variables or URL steps to manage a multi-step form.
  - Step 1: Create `Team` with `is_registered=False` and the leader's ID.
  - Step 2: Formset or iterative form to add `TeamMember` instances. Validates missing fields.
  - Final Step: Checks `team.members.count() + 1 >= hackathon.min_team_size` and that all members have required fields. If valid, sets `team.is_registered = True` and redirects to the participant dashboard.
</action>
<acceptance_criteria>
- `backend/participant/forms.py` contains `class TeamRegistrationForm` and `class TeamMemberForm`.
- `backend/participant/views.py` contains `class HackathonListView(ListView)` and `class HackathonRegisterWizardView(View)`.
</acceptance_criteria>
</task>

## 3. URL Routing

<task>
<read_first>
- backend/participant/urls.py
- backend/syntra/urls.py
</read_first>
<action>
Modify `backend/participant/urls.py` (create if missing, and ensure included in main `urls.py`):
- Map path `hackathons/` to `HackathonListView.as_view()`, name=`hackathon-list`.
- Map path `hackathons/<int:pk>/register/` to `HackathonRegisterWizardView.as_view()`, name=`hackathon-register`.
</action>
<acceptance_criteria>
- `backend/participant/urls.py` contains `path('hackathons/', ` and `path('hackathons/<int:pk>/register/', `.
</acceptance_criteria>
</task>

## 4. UI Implementation (Templates)

<task>
<read_first>
- .planning/phases/09-participant-join-registration-open-hackathon/09-UI-SPEC.md
- frontend/templates/accounts/dashboard.html
</read_first>
<action>
Create `frontend/templates/participant/hackathon_list.html`:
- Extend base layout (e.g., similar to dashboard).
- Use `bg-slate-950` for body.
- Display cards (`bg-slate-900/60`, `border-slate-700/60`) for each hackathon.
- Show `hackathon.name`, dates, and `min_team_size` - `max_team_size`.
- Include a `.btn-primary` styled link to `/hackathons/<id>/register/` saying "Register".
- If no hackathons, show empty state: "No Open Hackathons" / "There are currently no hackathons open for registration. Check back later!".

Create `frontend/templates/participant/hackathon_register.html`:
- Multi-step UI (using JS to show/hide steps or server-rendered steps).
- Dominant colors: `bg-slate-950`, text `slate-200`. Buttons: `bg-teal-500`, `text-slate-900`.
- Validation errors should use `red-500`.
- The primary CTA should be "Complete Registration" on the final step. Secondary/intermediate is "Next Step".
</action>
<acceptance_criteria>
- `frontend/templates/participant/hackathon_list.html` exists and contains `bg-slate-950` and `No Open Hackathons`.
- `frontend/templates/participant/hackathon_register.html` exists and contains `Complete Registration`.
</acceptance_criteria>
</task>

<threat_model>
- Injection: Standard Django ORM mitigates SQLi.
- XSS: Django templates auto-escape variables.
- Broken Access Control: Views must ensure the user is authenticated and has the `participant` role. The user cannot edit another team's draft or register for a closed hackathon.
</threat_model>

<schema_push_requirement>
**[BLOCKING] Schema Push Required**

This phase modifies schema-relevant files (backend/participant/models.py). The planner MUST include
a `[BLOCKING]` task that runs the database schema push command AFTER all schema file
modifications are complete but BEFORE verification.

- ORM detected: Django
- Push command: `python manage.py makemigrations && python manage.py migrate`
</schema_push_requirement>

## 5. Verification
- `python manage.py test participant` (if tests exist) or manually verify the `/hackathons/` route returns 200.
- Verify `is_registered` field is applied in DB schema.

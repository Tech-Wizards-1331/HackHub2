---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/models.py
  - backend/organizer/services/seating.py
  - backend/organizer/api_views.py
  - backend/organizer/urls.py
autonomous: true
---

# Phase 4: Integrate Seating Allocation System

<must_haves>
- Organizer can trigger seating allocation via API.
- The seating algorithm from the Flask app is accurately ported to Django.
- The allocation and room configuration are saved on the Hackathon model.
- An endpoint is provided to export the allocation as a CSV.
</must_haves>

<threat_model>
- High: Unauthorized users generating or exporting seating plans. Mitigated by strict IsAuthenticated and organizer-only permission checks on the API views.
- Medium: Extremely large JSON payloads for room configuration causing memory bloat. Mitigated by standard DRF payload size limits.
</threat_model>

<task>
<read_first>
- backend/organizer/models.py
- .planning/phases/04-integrate-seating-allocation-system-into-the-organizer-app/04-CONTEXT.md
</read_first>
<action>
Update the `Hackathon` model in `backend/organizer/models.py` to store seating configuration and results.
1. Add `room_configuration = models.JSONField(null=True, blank=True)` to the `Hackathon` model.
2. Add `seating_allocation = models.JSONField(null=True, blank=True)` to the `Hackathon` model.
3. Run `python manage.py makemigrations organizer` to generate the migration file.
</action>
<acceptance_criteria>
- `backend/organizer/models.py` contains `room_configuration = models.JSONField`
- `backend/organizer/models.py` contains `seating_allocation = models.JSONField`
- A new migration file is created in `backend/organizer/migrations/` containing these fields.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/participant/models.py
- hackathon_allotment/app.py
</read_first>
<action>
Create the seating service module at `backend/organizer/services/seating.py`.
1. Copy the `_build_bench_list` and `_allocate` functions from `hackathon_allotment/app.py` directly into this new file. Rename them to `build_bench_list` and `allocate`.
2. Create a new function `get_teams_for_allocation(hackathon_id)`:
   - Import `Team` from `participant.models`.
   - Query `Team.objects.filter(hackathon_id=hackathon_id).prefetch_related('members')`.
   - Format the result into a list of dicts: `[{"name": team.name, "members": ["Member 1 Name", "Member 2 Name", ...]}]`. Note that the algorithm expects the list of member names or identifiers. Since `TeamMember` has a `name` field, use `[member.name for member in team.members.all()]`.
   - If a team has no members, exclude it or just provide an empty list depending on algorithm safety (the algorithm skips empty `members`).
   - Also, include the Team Leader in the members list as the first member! `[team.leader.email] + [m.name for m in team.members.all()]`.
</action>
<acceptance_criteria>
- `backend/organizer/services/seating.py` exists.
- The file contains `def build_bench_list(rooms_config):`
- The file contains `def allocate(teams, rooms_config):`
- The file contains `def get_teams_for_allocation(hackathon_id):`
- `get_teams_for_allocation` queries the `Team` model and returns a list of dictionaries with `name` and `members` keys.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/api_views.py
- backend/organizer/services/seating.py
</read_first>
<action>
Create the API views in `backend/organizer/api_views.py`.
1. Create `AllocateSeatsView(APIView)`:
   - Requires `IsAuthenticated`.
   - In `post(self, request, hackathon_id)`:
     - Fetch the `Hackathon` ensuring `request.user.organizer_profile == hackathon.organizer`. Return 403 or 404 if not.
     - Expect `rooms_config` in `request.data`. If provided, save it to `hackathon.room_configuration` and `hackathon.save()`.
     - If not provided, try to use `hackathon.room_configuration`. If both are empty, return 400.
     - Call `get_teams_for_allocation(hackathon_id)` to get the teams list.
     - Call `allocate(teams, rooms_config)` from the service.
     - Save the result to `hackathon.seating_allocation` and `hackathon.save()`.
     - Return the allocation result with status 200.
2. Create `ExportSeatingCSVView(APIView)`:
   - Requires `IsAuthenticated`.
   - In `get(self, request, hackathon_id)`:
     - Fetch `Hackathon`, check permissions.
     - If `hackathon.seating_allocation` is None, return 400.
     - Create a CSV response (`HttpResponse(content_type='text/csv')`).
     - Set header `Content-Disposition: attachment; filename="seating_export.csv"`.
     - Write headers: `['Room', 'Section', 'Row', 'Bench', 'Team', 'Member']`.
     - Iterate through `hackathon.seating_allocation['teams']` (or `room_view` if easier) and write rows for each allocated seat. The algorithm returns `teams` with `seats` lists. For each team, for each seat block, for each member... Actually, `room_view` is easier to iterate. Iterate `room_view` -> `rooms` -> `rows` -> `benches` -> `assigned`.
     - For each `assigned` entry (`{"member": "...", "team": "..."}`), write a row.
     - Return the HTTP response.
</action>
<acceptance_criteria>
- `backend/organizer/api_views.py` contains `class AllocateSeatsView(APIView):`
- `AllocateSeatsView` saves `seating_allocation` to the Hackathon.
- `backend/organizer/api_views.py` contains `class ExportSeatingCSVView(APIView):`
- `ExportSeatingCSVView` returns an `HttpResponse` with `text/csv` content type.
</acceptance_criteria>
</task>

<task>
<read_first>
- backend/organizer/urls.py
</read_first>
<action>
Register the new endpoints in `backend/organizer/urls.py`.
1. Import `AllocateSeatsView` and `ExportSeatingCSVView`.
2. Add path `hackathons/<int:hackathon_id>/allocate-seats/`, mapped to `AllocateSeatsView.as_view()`, name `allocate-seats`.
3. Add path `hackathons/<int:hackathon_id>/seating-export/`, mapped to `ExportSeatingCSVView.as_view()`, name `seating-export`.
</action>
<acceptance_criteria>
- `backend/organizer/urls.py` contains path for `allocate-seats/`
- `backend/organizer/urls.py` contains path for `seating-export/`
</acceptance_criteria>
</task>

<verification_criteria>
- Models migrate successfully: `python manage.py makemigrations --dry-run` shows no issues.
- The syntax is correct and Django starts without errors.
- (Manual) User can POST to `/api/organizer/hackathons/<id>/allocate-seats/` with a valid payload and receive a 200 JSON response containing the layout.
</verification_criteria>

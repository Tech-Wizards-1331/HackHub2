# Phase 4 Research: Seating Allocation Integration

## Objective
Research how to implement Phase 4: integrate seating allocation system into the organizer app. 
"What do I need to know to PLAN this phase well?"

## Overview
Integrate the Python seating allocation algorithm from `hackathon_allotment/app.py` into the Django `organizer` app. The algorithm uses room configurations and team sizes to allocate seats optimally, keeping teams together as much as possible.

## Technical Approach

### 1. Service Layer (`organizer/services/seating.py`)
- Port `_build_bench_list` and `_allocate` directly from `hackathon_allotment/app.py`. The logic is pure Python and easily portable.
- Create a data-fetching adapter: Instead of parsing CSV files (`_parse_teams`), we need `get_teams_for_allocation(hackathon_id)` that queries `Team.objects.filter(hackathon_id=...)` and shapes it into the expected list of dictionaries (`[{"name": "Team A", "members": ["M1", "M2"]}]`). Note that `TeamMember` acts as guest records.

### 2. Model Updates (`organizer/models.py`)
- Update the `Hackathon` model to store the state.
- Add `room_configuration = models.JSONField(null=True, blank=True)` (input layout).
- Add `seating_allocation = models.JSONField(null=True, blank=True)` (calculated output).
- This aligns with the CONTEXT.md decision to persist these statelessly as JSON on the model rather than creating complex `Room`/`Bench` relations.

### 3. API Endpoints (`organizer/api_views.py`)
- **`POST /api/organizer/hackathons/<id>/allocate-seats/`**: 
  - Accepts `rooms_config` JSON payload.
  - Updates `Hackathon.room_configuration` if provided.
  - Calls the seating service.
  - Saves the output to `Hackathon.seating_allocation`.
  - Returns the JSON representation of the allocation map.
- **`GET /api/organizer/hackathons/<id>/seating-export/`**:
  - Retrieves the saved `seating_allocation`.
  - Transforms the nested JSON structure into a flat CSV format (Room, Row, Bench, Team, Member).
  - Returns an `HttpResponse` with `text/csv` content type.

### 4. Integration Points & Constraints
- The `organizer` app must import `Team` from the `participant` app.
- Permissions: These endpoints must be protected by `IsAuthenticated` and a custom permission ensuring the requesting user is the organizer of the specific hackathon.

## Risks & Edge Cases
- **Data Shape Mismatch:** The algorithm expects specific dict keys. The adapter function must strictly map Django model attributes to these keys.
- **Changed Team Sizes:** If a team adds a member after allocation, the saved JSON allocation will be out of sync. As decided in CONTEXT.md, the organizer manually re-running the allocation handles this.
- **Algorithm Performance:** The algorithm is fast, but doing synchronous allocation for thousands of participants in a web request might timeout. Given typical hackathon sizes (<1000 participants), synchronous processing is acceptable for now. No background task needed yet.

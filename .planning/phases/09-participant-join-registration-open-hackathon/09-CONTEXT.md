# Phase 9: participant join registration open hackathon - Context

**Gathered:** 2026-05-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Participant discovery and registration flow for open hackathons. Includes the global list of hackathons, team creation flow (as teams are required for registration), and guest record additions for teammates.

</domain>

<decisions>
## Implementation Decisions

### Discovery / Entry Point
- Use a global list page (`/hackathons`) showing all active hackathons.
- Hackathon card/preview should display: Name, dates, team size limits, and a brief description.

### Team Creation Flow
- Use a multi-step wizard for team registration (e.g., Step 1: Team Name, Step 2: Add Members).
- Save the team in a draft state as soon as the team name is entered, saving members incrementally.
- The team only becomes officially registered when the leader clicks "Complete Registration". (Requires a status or is_registered flag on the Team model).

### Guest Record Validation
- During the draft state, only Email and Name are required initially for guest teammates.
- All other fields (Skills, College, Semester, Degree) must be filled before completing registration.

### Validation & Enforcement
- Enforce strict email uniqueness per hackathon (a user/email can only be on one team per hackathon).
- Prevent clicking "Complete Registration" until the total team size (leader + guests) meets the `min_team_size` requirement of the hackathon.

### the agent's Discretion
- Form styling and exact wizard UI layout.
- Error message copy for validation failures.
- Empty states for the global hackathon list.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Hackathon & Team Models
- `backend/organizer/models.py` — Defines `Hackathon` (status `registration_open`, `min_team_size`, `max_team_size`).
- `backend/participant/models.py` — Defines `Team` and `TeamMember` (guest records) models.

### Project Requirements
- `.planning/REQUIREMENTS.md` — Specifically TEAM-01, TEAM-02 constraints on team leader registering and teammates as guest records.
- `.planning/PROJECT.md` — Constraint: Strictly separate identities for roles.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Dashboard layout and UI components (from `frontend/templates/accounts/dashboard.html`) can be used to style the wizard steps.
- Primary buttons (`.btn-primary`) and form field styles from recent organizer UI updates.

### Established Patterns
- Django views returning HTML templates.
- Django Forms / ModelForms for validation.

### Integration Points
- `/hackathons` URL needs to be created or updated to point to the new global list view.
- Registration link on the hackathon detail page points to the wizard view.

</code_context>

<deferred>
## Deferred Ideas

- Solo participants registering without a team (enforced to form a team of size `min_team_size`).
- Automatic team matching.

</deferred>

---

*Phase: 09-participant-join-registration-open-hackathon*
*Context gathered: 2026-05-15*

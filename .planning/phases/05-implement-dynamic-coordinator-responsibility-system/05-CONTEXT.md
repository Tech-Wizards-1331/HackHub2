# Phase 05: IMPLEMENT DYNAMIC COORDINATOR RESPONSIBILITY SYSTEM - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Evolve the coordinator model from a static role to a dynamic, scoped responsibility system. Coordinators will manage only their assigned areas within a hackathon via shared API endpoints, while organizers maintain full access to assign and revoke these responsibilities.
</domain>

<decisions>
## Implementation Decisions

### Responsibility Data Model
- **D-01:** Use a strict `TextChoices` enum (`Responsibility`) on the `HackathonCoordinator` model to define and validate allowed responsibilities (e.g., `PROBLEM_STATEMENTS`, `ANALYTICS`, `TEAM_MANAGEMENT`).

### Permission Enforcement
- **D-02:** Create a reusable custom DRF Permission Class (e.g., `HasResponsibility`) that hooks into `has_permission()` and `has_object_permission()` to cleanly gate access.

### API Surface Area
- **D-03:** Share the existing `/api/organizer/` endpoint namespace. Both Organizers and Coordinators will use the same endpoints, differentiated only by the new DRF permission classes.

### Dashboard Data Contract
- **D-04:** Provide a rich dashboard API response. Include both the assigned hackathon/responsibilities AND summary statistics (e.g., counts for problem statements, teams) relevant to their assigned areas.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Core
- `.planning/PROJECT.md` — Core value and role architecture constraints

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `organizer/api_views.py` — Existing viewsets (like `ProblemStatementViewSet`) that need their `permission_classes` updated.
- `accounts/decorators.py` — Contains `@role_required` pattern (though we decided on DRF classes, this shows existing auth patterns).

### Established Patterns
- `HackathonCoordinator.responsibilities` JSONField already exists.
- The `assign_coordinator` action already accepts a `responsibilities` array.
</code_context>

<specifics>
## Specific Ideas

No specific UI/UX references — this is primarily a backend API and permissions architectural phase.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.
</deferred>

---

*Phase: 05-implement-dynamic-coordinator-responsibility-system*
*Context gathered: 2026-04-23*

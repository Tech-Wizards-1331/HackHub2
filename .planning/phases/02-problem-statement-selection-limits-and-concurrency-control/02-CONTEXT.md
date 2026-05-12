# Phase 2: Problem Statement Selection Limits and Concurrency Control - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Adding capacity limits to problem statements and securely managing team selection under high concurrency.
</domain>

<decisions>
## Implementation Decisions

### Changing Selections
- **D-01:** Once a team selects a problem statement, it is locked in forever. They cannot change it.

### Limit Configuration
- **D-02:** The `max_teams_allowed` limit is REQUIRED for every problem statement. Organizers must specify a number.

### Error Experience
- **D-03:** If a team hits a race condition (e.g., last slot taken right as they click), the API should return a standard 400 Bad Request with a clear validation error (e.g., "This problem statement has reached its capacity limit.").

### The Agent's Discretion
- Database concurrency mechanism (e.g., `select_for_update()`, atomic transactions).
- Validation implementation details in DRF.
</decisions>

<specifics>
## Specific Ideas

- The system must always guarantee that the number of selected teams never exceeds the allowed limit, using proper locking or transactional control to avoid race conditions.
</specifics>

<canonical_refs>
## Canonical References

No external specs — requirements are fully captured in decisions above.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `organizer.ProblemStatement` exists and needs a new `max_teams_allowed` field.
- `participant.Team` exists and needs a relation to `ProblemStatement`.

### Established Patterns
- DRF ViewSets and standard ModelSerializers.

### Integration Points
- Team selection endpoint (likely on `TeamViewSet` or a custom action).
</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.
</deferred>

---

*Phase: 02-problem-statement-selection-limits-and-concurrency-control*
*Context gathered: 2026-04-30*

# Phase 3: Caching for Reads and Database for Writes - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement a Cache-Aside pattern with Write-Through invalidation for Hackathon Problem Statements. This allows participants to read the list of problem statements instantly without hitting the database, while ensuring the cache is accurately invalidated when a team selects a problem statement.

</domain>

<decisions>
## Implementation Decisions

### Cache Backend
- **Redis**: Use Redis as the cache backend (via `django-redis`). This is the industry standard for production and allows for distributed scaling.

### Cache Invalidation Scope
- **Entire List**: Cache the complete list of problem statements under a single key (e.g., `problem_statements_list_{hackathon_id}`).
- Invalidation must happen synchronously within the atomic transaction inside `TeamViewSet.select_problem_statement` to ensure data integrity immediately after a team makes a selection.

### Participant Read Endpoint
- **New Dedicated Endpoint**: Create a new `ReadOnlyModelViewSet` (or similar Read-Only endpoint) specifically for Participants inside `participant/api_views.py`.
- This maintains strict separation of concerns from the Organizer's CRUD endpoints.

### the agent's Discretion
- Exact Redis connection configuration for local development vs production (Render).
- Cache timeout duration (e.g., 5 minutes, 15 minutes) as a fallback if explicit invalidation is missed.
- The specific naming convention for cache keys.

</decisions>

<canonical_refs>
## Canonical References

### Project State
- `.planning/PROJECT.md` — Explains the requirement for strict separation between Organizer and Participant endpoints.
- `.planning/REQUIREMENTS.md` — Outlines HACK-04 (Problem Statement management).

</canonical_refs>

<specifics>
## Specific Ideas

- Keep the caching logic isolated so it doesn't leak into the models; use standard `django.core.cache`.
- Make sure to namespace cache keys by Hackathon ID, so caching the list for one hackathon doesn't bleed into another.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-caching-for-reads-and-database-for-writes-properly-you-follo*
*Context gathered: 2026-04-30*

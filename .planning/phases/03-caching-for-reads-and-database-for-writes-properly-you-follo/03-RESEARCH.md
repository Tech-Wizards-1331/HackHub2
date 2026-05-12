# Phase 3: Caching for Reads and Database for Writes - Research

## Context
This phase implements a Cache-Aside pattern with Write-Through invalidation for Hackathon Problem Statements. The goal is to allow participants to quickly read problem statements without hitting the database, while ensuring the cache is accurately invalidated when a team selects a problem statement.

## Current State Analysis
1. **Cache Configuration:** `backend/syntra/settings.py` does not currently define `CACHES`. We need to add `django-redis` as the cache backend.
2. **Missing Endpoint:** There is no Read-Only endpoint for Participants to fetch problem statements. Only `organizer.api_views.ProblemStatementViewSet` exists, which is strictly for organizers.
3. **Missing Serializer Fields:** The `organizer.api_serializers.ProblemStatementSerializer` is missing the `max_teams_allowed` field added in Phase 2.
4. **Data Needs for Participants:** Participants need to know if a problem statement is "full" (reached capacity). The new participant endpoint should return the current count of teams that selected it (`selected_by_teams.count()`), or at least an `is_full` boolean, by annotating the queryset.

## Validation Architecture (Nyquist)
- [ ] Redis is configured as the default cache in `settings.py`.
- [ ] A new `ReadOnlyModelViewSet` exists in `participant/api_views.py` for Problem Statements.
- [ ] The participant endpoint fetches from the cache first; if missing, fetches from DB, caches it, and returns.
- [ ] `select_problem_statement` in `participant/api_views.py` calls `cache.delete()` for the specific hackathon's problem statement list after a successful transaction.
- [ ] The cached data is correctly namespaced by hackathon ID (`problem_statements_list_{hackathon_id}`).

## Dependencies
- `django-redis` needs to be added to `requirements.txt`.
- Redis server needs to be available (or default to LocalMemCache for local dev if Redis is unavailable, but the context decision specified Redis).

## Blockers / Risks
- If we annotate the queryset with `Count('selected_by_teams')` *before* caching, the cache will hold stale counts until a new team selects *that specific problem statement*. However, since we invalidate the *entire list* cache (`problem_statements_list_{hackathon_id}`) whenever *any* team in that hackathon makes a selection, the counts will refresh precisely when they change! This is a perfect synergy between the "entire list" invalidation scope and the need for accurate counts.

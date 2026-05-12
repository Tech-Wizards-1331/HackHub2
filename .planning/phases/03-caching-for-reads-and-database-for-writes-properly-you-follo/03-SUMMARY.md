# Phase 3: Caching for Reads and Database for Writes — Summary

**Completed:** 2026-04-30

## What Was Built

Implemented a **Cache-Aside pattern** with **Write-Through invalidation** for Hackathon Problem Statements, allowing participants to read problem statement lists at sub-millisecond speed while maintaining strict data integrity on writes.

## Key Changes

### 1. Redis Cache Backend (`backend/syntra/settings.py`)
- Added `CACHES` configuration with Redis (`django-redis`) when `REDIS_URL` is set.
- Falls back to Django's `LocMemCache` for local development without Redis.

### 2. Organizer Serializer Fix (`backend/organizer/api_serializers.py`)
- Added the `max_teams_allowed` field that was missing from Phase 2.

### 3. Participant Serializer (`backend/participant/api_serializers.py`)
- Created `ParticipantProblemStatementSerializer` with computed fields:
  - `current_teams_count` — how many teams have selected this statement.
  - `is_full` — boolean indicating if capacity is reached.

### 4. Cached Read Endpoint (`backend/participant/api_views.py`)
- Created `ParticipantProblemStatementViewSet` (ReadOnly).
- `list()` checks cache first → returns instantly on hit.
- On miss, queries DB with annotated counts → caches → returns.
- Endpoint: `GET /api/participant/problem-statements/?hackathon_id=X`

### 5. Cache Invalidation (`backend/participant/api_views.py`)
- `select_problem_statement` now calls `cache.delete()` inside the atomic transaction block.
- Cache key: `problem_statements_list_{hackathon_id}` — precisely scoped per hackathon.

### 6. URL Routing (`backend/participant/api_urls.py`)
- Registered `ParticipantProblemStatementViewSet` at `problem-statements/`.

## Verification
- `python manage.py check` — 0 issues.
- All 6 files modified as planned.

## Self-Check: PASSED

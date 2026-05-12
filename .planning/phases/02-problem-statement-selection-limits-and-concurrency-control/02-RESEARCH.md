# Phase 2: Problem Statement Selection Limits and Concurrency Control - Research

## Overview
This document outlines the technical research for implementing capacity limits and concurrency-safe selection for Problem Statements by Teams.

## Architecture & Data Model

### 1. `ProblemStatement` Model (organizer app)
- Add `max_teams_allowed = models.PositiveIntegerField()` field.
- By design (D-02), this is a REQUIRED field, meaning `null=False, blank=False`.
- For existing problem statements (migration), a default value will need to be provided (e.g., `default=10` or a dummy value).

### 2. `Team` Model (participant app)
- Add `selected_problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.SET_NULL, null=True, blank=True, related_name='selected_by_teams')`
- Need to enforce rule D-01: Once selected, it cannot be changed. This is enforced at the API layer (and potentially `clean()` method).

## Concurrency Control Strategy

To prevent race conditions when multiple teams select a problem statement simultaneously:
- Use `django.db.transaction.atomic()`
- Use `ProblemStatement.objects.select_for_update().get(id=ps_id)` to acquire a database-level row lock.
- With the lock held, check the current count: `ps.selected_by_teams.count() >= ps.max_teams_allowed`.
- If limit reached, return HTTP 400 with a clean DRF `ValidationError`.
- If limit not reached, assign `team.selected_problem_statement = ps` and save the team.
- The row lock automatically releases when the transaction commits or rolls back.

## API Integration

- **Endpoint:** Create a custom DRF action on `TeamViewSet`, e.g., `@action(detail=True, methods=['post']) def select_problem_statement(self, request, pk=None)`.
- **Validation:**
    1. Check if team already has a problem statement (enforces D-01).
    2. Start atomic transaction.
    3. `select_for_update()` the requested problem statement.
    4. Check if count >= `max_teams_allowed`. Raise DRF ValidationError if so (enforces D-03).
    5. Save the relation.

## Validation Architecture (Nyquist)
- Dimensions: Concurrency & Load (ensuring race conditions handle cleanly under concurrent requests).
- Validation points: Unit tests using threading/multiprocessing or explicit transaction testing to verify the lock holds and limits are strictly enforced.

## Dependencies
- Modifies `organizer.models` and `participant.models`.
- Requires `makemigrations` and `migrate` for both apps.

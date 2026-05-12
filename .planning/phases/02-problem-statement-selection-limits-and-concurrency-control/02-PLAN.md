---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/models.py
  - backend/participant/models.py
  - backend/participant/api_serializers.py
  - backend/participant/api_views.py
autonomous: true
---

# Phase 2: Problem Statement Selection Limits and Concurrency Control - Plan

## Verification Criteria
- [ ] ProblemStatement has `max_teams_allowed` field.
- [ ] Team has `selected_problem_statement` ForeignKey.
- [ ] Endpoint allows selecting a problem statement safely using `select_for_update()`.
- [ ] Returns HTTP 400 when selection limit is reached.
- [ ] Team cannot change their problem statement once selected.

## Must Haves
- Atomic transactions.
- Strict limit enforcement.
- Immutable team selection.

## Tasks

```xml
<task>
  <id>update-models</id>
  <description>Add limits to ProblemStatement and problem_statement relation to Team</description>
  <read_first>
    - backend/organizer/models.py
    - backend/participant/models.py
  </read_first>
  <action>
    Modify backend/organizer/models.py:
    - Add `max_teams_allowed = models.PositiveIntegerField(default=10)` to `ProblemStatement`. (Default required for existing rows).
    
    Modify backend/participant/models.py:
    - Add `selected_problem_statement = models.ForeignKey('organizer.ProblemStatement', on_delete=models.SET_NULL, null=True, blank=True, related_name='selected_by_teams')` to `Team`.
  </action>
  <acceptance_criteria>
    - `grep "max_teams_allowed = models.PositiveIntegerField" backend/organizer/models.py` exits 0.
    - `grep "selected_problem_statement = models.ForeignKey" backend/participant/models.py` exits 0.
  </acceptance_criteria>
</task>

<task>
  <id>makemigrations-migrate</id>
  <description>Generate and apply migrations</description>
  <read_first>
    - backend/manage.py
  </read_first>
  <action>
    Run `python manage.py makemigrations` and `python manage.py migrate` in the `backend` directory to apply the model changes.
  </action>
  <acceptance_criteria>
    - Commands execute without errors.
  </acceptance_criteria>
</task>

<task>
  <id>implement-selection-api</id>
  <description>Implement thread-safe selection API in TeamViewSet</description>
  <read_first>
    - backend/participant/api_views.py
    - backend/participant/api_serializers.py
  </read_first>
  <action>
    Modify backend/participant/api_serializers.py:
    - Expose `selected_problem_statement` on `TeamSerializer` (read-only).
    - Create a minimal serializer `TeamProblemStatementSelectSerializer` with a single `problem_statement_id` integer field to accept input.

    Modify backend/participant/api_views.py:
    - Add `@action(detail=True, methods=['post'])` named `select_problem_statement` to `TeamViewSet`.
    - Validate input using `TeamProblemStatementSelectSerializer`.
    - Check if `team.selected_problem_statement` is already set. If so, `raise ValidationError("Problem statement is already locked in and cannot be changed.")`.
    - Open `with transaction.atomic():`
    - Fetch problem statement with lock: `ps = ProblemStatement.objects.select_for_update().get(id=ps_id)`
    - Check capacity: `if ps.selected_by_teams.count() >= ps.max_teams_allowed:`
    - If full, `raise ValidationError({"detail": "This problem statement has reached its capacity limit."})`
    - Else, set `team.selected_problem_statement = ps`, call `team.save(update_fields=['selected_problem_statement'])`, and return `Response({"status": "success"})`.
  </action>
  <acceptance_criteria>
    - `grep "@action(detail=True, methods=\['post'\])" backend/participant/api_views.py` exits 0.
    - `grep "select_for_update()" backend/participant/api_views.py` exits 0.
    - `grep "transaction.atomic()" backend/participant/api_views.py` exits 0.
  </acceptance_criteria>
</task>
```

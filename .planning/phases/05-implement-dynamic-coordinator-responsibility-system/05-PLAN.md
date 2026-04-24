---
phase: 05
status: draft
wave: 1
depends_on: []
files_modified:
  - backend/organizer/models.py
  - backend/organizer/permissions.py
  - backend/organizer/api_views.py
  - backend/organizer/api_serializers.py
  - backend/organizer/tests.py
autonomous: true
---

# Phase 05: IMPLEMENT DYNAMIC COORDINATOR RESPONSIBILITY SYSTEM

## Goal
Allow organizers to assign multiple scoped responsibilities to coordinators within a hackathon, replacing static roles with a dynamic, responsibility-based permission system that operates securely on shared API endpoints.

## Requirements Covered
- D-01: Strict TextChoices enum for responsibilities
- D-02: Reusable DRF Permission Classes
- D-03: Shared API endpoint namespace
- D-04: Rich Dashboard API endpoint

## Threat Model
- **T-05-01 (Privilege Escalation):** Coordinator accessing endpoints for responsibilities they do not possess. Mitigated by `HasResponsibility` permission checks.
- **T-05-02 (Horizontal Data Leak):** Coordinator accessing data for a hackathon they are not assigned to. Mitigated by strict `get_queryset` modifications returning only assigned hackathons.

## Tasks

### Wave 1: Data Model and Permission Core

```xml
<task id="05-01-01" autonomous="true">
  <read_first>
    - backend/organizer/models.py
  </read_first>
  <action>
    Add a nested `TextChoices` enum to the `HackathonCoordinator` model in `backend/organizer/models.py` named `Responsibility`.
    It must contain three choices: `PROBLEM_STATEMENTS = 'PROBLEM_STATEMENTS', 'Problem Statements'`, `ANALYTICS = 'ANALYTICS', 'Analytics'`, and `TEAM_MANAGEMENT = 'TEAM_MANAGEMENT', 'Team Management'`.
  </action>
  <acceptance_criteria>
    - `grep -q "class Responsibility(models.TextChoices):" backend/organizer/models.py`
    - `grep -q "PROBLEM_STATEMENTS" backend/organizer/models.py`
  </acceptance_criteria>
</task>

<task id="05-01-02" autonomous="true">
  <read_first>
    - backend/organizer/api_views.py
    - backend/organizer/models.py
  </read_first>
  <action>
    Create a new file `backend/organizer/permissions.py`.
    Implement `class IsOrganizerOrHasResponsibility(permissions.BasePermission):`.
    It should allow access if `request.user.role == User.Role.ORGANIZER`.
    If the user is a `COORDINATOR`, it must check `HackathonCoordinator` to verify the user is assigned to the related hackathon and their `responsibilities` array contains `self.responsibility_required`.
    Create a subclass `class CanManageProblemStatements(IsOrganizerOrHasResponsibility):` with `responsibility_required = HackathonCoordinator.Responsibility.PROBLEM_STATEMENTS`.
  </action>
  <acceptance_criteria>
    - `cat backend/organizer/permissions.py | grep "class IsOrganizerOrHasResponsibility"`
    - `cat backend/organizer/permissions.py | grep "class CanManageProblemStatements"`
  </acceptance_criteria>
</task>

<task id="05-01-03" autonomous="true">
  <read_first>
    - backend/organizer/api_views.py
  </read_first>
  <action>
    Update the `assign_coordinator` action in `HackathonViewSet` (`backend/organizer/api_views.py`).
    Extract `valid_resps = [c[0] for c in HackathonCoordinator.Responsibility.choices]`.
    Iterate over the incoming `responsibilities` list from `request.data`. If any responsibility is not in `valid_resps`, return a 400 Bad Request: `Response({'error': f'Invalid responsibility: {r}'}, status=status.HTTP_400_BAD_REQUEST)`.
  </action>
  <acceptance_criteria>
    - `grep -q "Invalid responsibility" backend/organizer/api_views.py`
  </acceptance_criteria>
</task>
```

### Wave 2: API Surface Updates

```xml
<task id="05-02-01" autonomous="true">
  <read_first>
    - backend/organizer/api_views.py
    - backend/organizer/permissions.py
  </read_first>
  <action>
    Update `ProblemStatementViewSet` in `backend/organizer/api_views.py`.
    Change `permission_classes = [IsOrganizer]` to `permission_classes = [CanManageProblemStatements]` (import it from `.permissions`).
    Update `get_queryset()` to return statements where `hackathon__organizer__user=self.request.user` OR `hackathon__coordinators__user=self.request.user`.
    Update `_get_hackathon()` similarly: fetch using a `Q` object `Q(organizer__user=self.request.user) | Q(coordinators__user=self.request.user)`.
  </action>
  <acceptance_criteria>
    - `grep -q "CanManageProblemStatements" backend/organizer/api_views.py`
    - `grep -q "Q(organizer__user=self.request.user) | Q(coordinators__user=self.request.user)" backend/organizer/api_views.py`
  </acceptance_criteria>
</task>

<task id="05-02-02" autonomous="true">
  <read_first>
    - backend/organizer/api_views.py
  </read_first>
  <action>
    Update `HackathonViewSet.get_queryset` to return hackathons for both organizers and coordinators: `return Hackathon.objects.filter(Q(organizer__user=self.request.user) | Q(coordinators__user=self.request.user)).distinct()`.
    Update the `HackathonViewSet.permission_classes` to allow both Organizers and Coordinators (create a generic `IsOrganizerOrCoordinator` permission in `.permissions` if needed, and apply it here). Note: `perform_create` and other mutative endpoints on the Hackathon itself should still be protected so Coordinators cannot delete/edit the hackathon details itself. Either override `get_permissions` or handle carefully. For simplicity, create `class IsOrganizerOrReadOnlyCoordinator(permissions.BasePermission)` in `permissions.py` and set it as the default permission for `HackathonViewSet`. Ensure `assign_coordinator` and `unassign_coordinator` are decorated with `@action(..., permission_classes=[IsOrganizer])`.
  </action>
  <acceptance_criteria>
    - `grep -q "IsOrganizerOrReadOnlyCoordinator" backend/organizer/permissions.py`
    - `grep -q "permission_classes=\[IsOrganizer\]" backend/organizer/api_views.py`
  </acceptance_criteria>
</task>

<task id="05-02-03" autonomous="true">
  <read_first>
    - backend/organizer/api_views.py
  </read_first>
  <action>
    Add a new action `@action(detail=False, methods=['get'])` named `coordinator_dashboard` to `HackathonViewSet` in `backend/organizer/api_views.py`.
    It must return a JSON response containing an array of the coordinator's assignments. 
    Each object should include:
    `"hackathon": HackathonSerializer(h).data`,
    `"responsibilities": assignment.responsibilities`,
    `"stats": {"problem_statements_count": h.problem_statements.count()}`.
    It should filter `HackathonCoordinator.objects.filter(user=request.user).select_related('hackathon')`.
  </action>
  <acceptance_criteria>
    - `grep -q "def coordinator_dashboard" backend/organizer/api_views.py`
    - `grep -q "problem_statements_count" backend/organizer/api_views.py`
  </acceptance_criteria>
</task>
```

### Wave 3: Testing and Verification

```xml
<task id="05-03-01" autonomous="true">
  <read_first>
    - backend/organizer/tests.py
  </read_first>
  <action>
    Add comprehensive tests to `backend/organizer/tests.py` ensuring that:
    1. A coordinator with `PROBLEM_STATEMENTS` responsibility can successfully POST to `/api/organizer/hackathons/{id}/problem-statements/`.
    2. A coordinator WITHOUT `PROBLEM_STATEMENTS` receives a 403 Forbidden.
    3. An organizer can always POST regardless of coordinator presence.
    4. The `/api/organizer/hackathons/coordinator_dashboard/` endpoint returns the correct structure and counts.
    5. `assign_coordinator` rejects invalid responsibilities like `['FAKE_RESP']` with a 400 error.
  </action>
  <acceptance_criteria>
    - `python manage.py test organizer.tests` passes successfully.
  </acceptance_criteria>
</task>
```

## Must Haves
- Responsibility enum validation on assignment.
- DRF permissions blocking unauthorized coordinators from restricted namespaces.
- Organizers retaining full access implicitly.
- Coordinator Dashboard endpoint returning rich statistics.

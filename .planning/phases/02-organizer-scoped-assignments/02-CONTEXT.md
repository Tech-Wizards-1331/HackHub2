# Phase 2: Organizer Scoped Assignments (Refinement)

## Goal
Enable Sub-Admins in the organizer app to securely scope, list, and manage coordinators for their specific hackathons, including granular responsibility assignment.

## Requirements
- [ORG-01]: Sub-Admins can assign users as Coordinators for a specific hackathon (Backend done in P1, UI needed in P2).
- [ORG-02]: System enforces scoped permissions (Backend done in P1).
- [ORG-03]: Sub-Admins have a UI to manage/assign Coordinators within the Organizer dashboard.

## Deliverables

### 1. Backend Refinements (Organizer API)
- **HackathonViewSet Actions**:
    - `list_coordinators`: Returns all `HackathonCoordinator` records for a specific hackathon.
    - `unassign_coordinator`: Removes a coordinator assignment from a hackathon.
- **HackathonCoordinatorSerializer**: Update to include `responsibilities` field.

### 2. Frontend UI (Organizer Dashboard)
- **Coordinator Management Tab**:
    - List current coordinators for the selected hackathon.
    - View their assigned responsibilities (e.g., Problem Management, Analytics).
    - Remove a coordinator with a confirmation prompt.
    - Assign new coordinators via email with responsibility checkboxes:
        - `problem_statements`
        - `teams`
        - `analytics`

## Success Criteria
1. Sub-Admin can see a list of assigned coordinators for any of their hackathons.
2. Sub-Admin can unassign a coordinator, and that coordinator immediately loses access to that hackathon's dashboard data.
3. Sub-Admin can update/set responsibilities during assignment.

## Technical Notes
- Use `JSONField` for responsibilities in `HackathonCoordinator`.
- Frontend uses Vanilla JS `fetch()` with JWT authentication.
- Scoping ensures organizers can only list/unassign coordinators for hackathons they own.

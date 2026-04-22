# Phase 2 Validation Strategy

## Test Infrastructure
- Framework: Django `TestCase`
- API Client: `rest_framework.test.APIClient`

## Automated Test Cases

### 1. Coordinator Management (Organizer API)
- **LIST**: Verify organizer can list coordinators for their hackathon.
- **LIST**: Verify organizer CANNOT list coordinators for a hackathon they don't own.
- **UNASSIGN**: Verify organizer can remove a coordinator assignment.
- **UNASSIGN**: Verify unassigned user still exists but is no longer linked to the hackathon.

## Manual UAT Criteria

| ID | Feature | Expected Behavior |
|----|---------|-------------------|
| ORG-UAT-01 | Coordinator List | The management modal shows a list of all users assigned to the hackathon with their emails and responsibilities. |
| ORG-UAT-02 | Granular Assignment | When assigning a coordinator, the organizer can toggle specific responsibilities (Problem Management, Analytics, etc.). |
| ORG-UAT-03 | Unassignment | Clicking "Unassign" removes the user from the list and revokes their scoped access immediately. |

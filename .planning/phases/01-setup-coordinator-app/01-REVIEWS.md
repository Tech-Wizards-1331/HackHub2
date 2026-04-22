---
phase: 1
reviewers: [gemini-pro]
reviewed_at: 2026-04-22T19:50:00Z
plans_reviewed: [01-01-PLAN.md]
---

# Cross-AI Plan Review — Phase 1

## Gemini Review

The implementation plan for the Coordinator App is solid, well-structured, and strictly adheres to the decisions made in the `CONTEXT.md` file. It breaks the work down logically into app creation, model updates, permissions, API views, and routing.

### Strengths
- **Clean separation of concerns:** Keeps the `HackathonCoordinator` assignment logic in the `organizer` app while placing the reading/dashboard logic in the `coordinator` app.
- **Robust permission system:** The `CoordinatorPermissionMixin` is an elegant solution to enforce both hackathon-level access and responsibility-level access in a reusable way.
- **Task-oriented dashboard:** The `CoordinatorDashboardSerializer` intelligently formats the response based on the coordinator's specific responsibilities.

### Concerns
- **HIGH: N+1 Query Problem in Dashboard:** The `CoordinatorDashboardViewSet.dashboard()` method retrieves hackathons but does not use `prefetch_related('problem_statements')`. Calling `obj.problem_statements.count()` and `obj.problem_statements.filter()` in the serializer will trigger separate database queries for every hackathon returned, leading to a severe N+1 performance issue.
- **MEDIUM: Destructive Role Reassignment:** The `assign_coordinator` action updates the user's role to `COORDINATOR` (`user.role = User.Role.COORDINATOR`). Since the system only allows a single global role per user, this will silently strip an Organizer or Judge of their existing role if they are assigned as a Coordinator. This needs explicit handling or a warning.
- **LOW: Missing `prefetch_related` for `user` on `CoordinatorProfileAdmin`:** The admin class specifies `list_display = ('user', 'created_at')`. It should specify `list_select_related = ('user',)` to avoid N+1 queries in the Django admin interface.

### Suggestions
- In Task `1-01-04`, update the `dashboard` action to use `.prefetch_related('problem_statements')` when querying hackathons.
- In Task `1-01-02`, consider adding a check to prevent reassigning users who are already `ORGANIZER` or `SUPER_ADMIN` to `COORDINATOR`, or document that this destructive change is accepted for Phase 1.
- In Task `1-01-01`, add `list_select_related = ('user',)` to `CoordinatorProfileAdmin`.

### Risk Assessment
**LOW.** The architectural approach is sound and relies on established DRF patterns. The N+1 query issue is the only significant technical risk, and it is easily fixed by adding a `prefetch_related` clause to the queryset.

---

## Consensus Summary

The plan is highly aligned with the required architecture and successfully implements the task-oriented dashboard and 3-layer permission system.

### Agreed Strengths
- Reusable `CoordinatorPermissionMixin` pattern.
- Dashboard API dynamically adjusts to responsibilities.
- Avoids over-engineering by keeping the `HackathonCoordinator` model in the `organizer` app.

### Agreed Concerns
- **N+1 Performance Risk:** The dashboard serializer will execute queries per hackathon for problem statement counts.
- **Role Assignment Conflict:** Assigning a coordinator strips them of any previous role, which could have unintended consequences for users with multiple hats.

### Recommendations for Replanning
1. Update `1-01-04` to ensure the dashboard queryset uses `prefetch_related`.
2. Update `1-01-02` to either prevent overwriting higher-level roles or explicitly handle the role transition safely.

# Code Review for Phase 09

## Summary of Findings

- **[Fixed]** **Duplicate Registration Vulnerability:** Found missing checks preventing a user from continuing to modify their team after registration was completed, or allowing a user to start a new draft while already belonging to a registered team.
- **[Fixed]** **Team Size Constraint UX/Logic Clarification:** Addressed confusion around `min_team_size` constraints. Improved the error messaging so it explicitly breaks down the count requirement (`Leader + X members`) and prevents scenarios where valid draft lengths appear to fail constraints.

## Actions Taken
- Added access control to `HackathonRegisterWizardView`'s `get` and `post` handlers. If `TeamMember.objects.filter(..., team__is_registered=True)` or `team.is_registered=True`, the request is redirected with a clear info message.
- Updated the min/max team size validation error messages to dynamically show the current total compared to the expected mathematical bounds.

# Phase 09: participant join registration open hackathon - Research

## Overview
This phase handles the participant flow to discover open hackathons and register by creating a team (or registering solo as a team of 1, given `min_team_size`). It involves the global list view, a multi-step registration wizard, and model updates to track registration drafts.

## Model Changes Required
1. **`participant.models.Team`**:
   - Add an `is_registered = models.BooleanField(default=False)` field (or a `status` choices field `draft` vs `registered`). The wizard will create the `Team` as `is_registered=False` immediately when step 1 (Team Name) is completed. When the final "Complete Registration" is clicked, it flips to `True`.

2. **`participant.models.TeamMember`**:
   - Needs validation to ensure email uniqueness *per hackathon*. `unique_together = ('team', 'email')` only prevents duplicates in the *same* team. We need validation (in the form and model `clean()` method) to prevent the same email from being registered across *different* teams in the same hackathon. 

## UI/UX Approaches (Reusable Assets)
- `frontend/templates/accounts/dashboard.html` uses a slate/teal color palette (`bg-slate-950`, `text-teal-400`, `animate-fade-in`), Tailwind classes, and glassmorphic panels (`bg-slate-900/60`, `backdrop-blur`).
- The multi-step wizard should be implemented as a Django view. We have two main approaches:
  1. **Django Form Wizard (django-formtools)**: Robust but heavy.
  2. **Custom Multi-step Views/State**: A single view rendering different steps via `?step=X` or POST states, saving the `Team` instance to the database immediately upon the first step. Given the CONTEXT decision ("save incrementally in draft state"), a standard stateful view sequence or single view with state parameters is easier than `formtools` because we want immediate database saves for the draft team.

## Views Needed
1. **`participant.views.HackathonListView`**:
   - Endpoint: `/hackathons/`
   - Purpose: Show all hackathons. Filter by `status='registration_open'` (or show all but disable registration for others).
2. **`participant.views.HackathonRegistrationWizard`**:
   - Endpoint: `/hackathons/<int:pk>/register/`
   - Purpose: Handle team name creation, adding members (via Django Formset or individual POSTs), and final completion.

## Constraints & Business Logic
- **`min_team_size` Enforcement**: The registration cannot be completed (cannot flip `is_registered=True`) unless `team.members.count() + 1 >= hackathon.min_team_size`.
- **Validation**: Guest records (TeamMembers) only require `email` and `name` to be saved in the draft. However, all fields must be filled before the final registration can occur. This suggests standard model validation might need `blank=True` for `college`, `semester`, `degree` initially, but the final submission view must validate that these fields are not empty before marking `is_registered=True`.

## Validation Architecture
- **Schema Validation**: Ensure `is_registered` is added via migration.
- **Form Validation**: `TeamMember` uniqueness per hackathon must be tested.
- **Workflow Validation**: End-to-end test of creating a team, adding a member with missing fields (fails final step), completing fields, and submitting successfully.

## Conclusion
The planner now has enough information to structure the `Team` modifications, the two primary views (list and wizard), and the strict validation rules required.

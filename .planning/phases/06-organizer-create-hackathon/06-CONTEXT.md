# Phase 6 Context: Organizer Create Hackathon

## Overview
This phase adds a Django template-based form that allows authenticated organizers to create new hackathons directly from their dashboard UI.

## Decisions Made

### 1. Form Implementation Approach
- **Decision:** Separate page at `/organizer/create-hackathon/` using a Django `CreateView`.
- **Rationale:** Follows the existing template pattern from Phase 5. Avoids JavaScript/modal complexity.

### 2. Form Fields Scope
- **Decision:** Essential fields only:
  - `name` (required)
  - `description` (optional)
  - `start_date` / `end_date` (required)
  - `registration_deadline` (required)
  - `min_team_size` / `max_team_size` (defaults: 1 and 4)
- **Auto-set fields:** `status` defaults to `registration_open`. `room_configuration` and `seating_allocation` are left null (configured later via API).
- **Rationale:** Keeps the form simple and focused on essential creation data.

### 3. Post-Creation Redirect
- **Decision:** Redirect to `/organizer/dashboard/` with a Django `messages.success()` flash message.
- **Rationale:** Immediate feedback — the new hackathon appears in the dashboard list.

## Code Context
- **Model:** `organizer.models.Hackathon` (already exists with all fields).
- **View:** New `CreateHackathonView` in `backend/organizer/views.py`.
- **Form:** New `HackathonForm` (ModelForm) in `backend/organizer/forms.py`.
- **Template:** New `backend/organizer/templates/organizer/create_hackathon.html`.
- **URL:** New path in `backend/organizer/urls.py`.
- **Dashboard Update:** Add a "Create Hackathon" button/link to existing `dashboard.html`.

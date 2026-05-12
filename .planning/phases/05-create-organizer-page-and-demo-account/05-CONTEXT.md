# Phase 5 Context: Organizer Page and Demo Account

## Overview
This phase implements the initial visual dashboard for hackathon organizers and creates a reusable mechanism to provision a specific demo account (`org@gmail.com`).

## Decisions Made

### 1. Frontend Implementation
- **Decision:** Use a basic Django Template (`organizer_dashboard.html`).
- **Rationale:** Provides immediate functional value without the overhead of setting up a separate frontend SPA or complex REST consumption for the initial page load.

### 2. Demo Account Provisioning Strategy
- **Decision:** Create a custom Django management command (`create_demo_organizer`).
- **Rationale:** Ensures the creation of the `org@gmail.com` (password: `Admin@123`) user is repeatable, idempotent, and cleanly separated from standard database migrations. It will also provision the necessary `OrganizerProfile` and assign the `organizer` role.

### 3. Organizer Page Scope
- **Decision:** The dashboard will display a basic overview: a welcome header and a list of hackathons belonging to the authenticated organizer.
- **Rationale:** Keeps the scope strictly to the core requirement of having an organizer page, mapping cleanly to the existing `Hackathon` model relationships.

## Canonical References
- None required (standard Django architecture).

## Code Context
- **Models:** `users.User` (custom auth model), `organizer.models.OrganizerProfile`, `organizer.models.Hackathon`.
- **Views:** Will need a new Django TemplateView or functional view in the `organizer` app.

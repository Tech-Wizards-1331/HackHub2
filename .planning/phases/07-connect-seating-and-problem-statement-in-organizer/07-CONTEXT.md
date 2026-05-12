# Phase 7 Context: Connect Seating & Problem Statement Management in Organizer

## Overview
This phase exposes the existing seating allocation and problem statement APIs through the organizer's template-based UI. A new Hackathon Detail page serves as the central hub for per-hackathon management.

## Decisions Made

### 1. Navigation Structure
- **Decision:** Each hackathon on the dashboard links to a detail page at `/organizer/hackathon/<id>/`.
- **Rationale:** Creates a natural drill-down flow: Dashboard → Hackathon Detail → Manage features.

### 2. Problem Statement Management UI
- **Decision:** Full template-based CRUD for problem statements on the hackathon detail page.
- **Rationale:** Self-contained UI — organizers don't need API/Postman knowledge.

### 3. Seating Allocation UI
- **Decision:** Simple JSON textarea for `room_configuration` + "Run Allocation" button. Results displayed in a readable table with CSV export link.
- **Rationale:** Avoids over-engineering a structured room builder form. The JSON input matches the existing API contract.

### 4. Scope of Hackathon Detail Page
- **Decision:** Read-only hackathon info (name, dates, status) at the top, with two management sections below: Problem Statements and Seating Allocation.
- **Rationale:** No hackathon edit capability in this phase — keeps scope focused.

## Code Context
- **Existing APIs:** Problem statement CRUD viewset at `organizer.api_views`, seating at `AllocateSeatsView` and `ExportSeatingCSVView`.
- **Models:** `Hackathon`, `ProblemStatement` in `organizer.models`.
- **Services:** `organizer.services.seating` for allocation algorithm.
- **New views needed:** `HackathonDetailView`, `AddProblemStatementView`, `DeleteProblemStatementView`, `RunSeatingAllocationView`.
- **New templates:** `hackathon_detail.html`, `add_problem_statement.html`.
- **Dashboard update:** Make hackathon names clickable links.

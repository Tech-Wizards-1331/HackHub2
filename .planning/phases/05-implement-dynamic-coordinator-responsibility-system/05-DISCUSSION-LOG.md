# Phase 05: IMPLEMENT DYNAMIC COORDINATOR RESPONSIBILITY SYSTEM - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 05-implement-dynamic-coordinator-responsibility-system
**Areas discussed:** Responsibility Enum vs Open-Ended, Permission Enforcement Pattern, Coordinator API Surface, Dashboard Data Contract

---

## Responsibility Enum vs Open-Ended

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Strict TextChoices enum — Define a `Responsibility` enum class on the model. Validate incoming values against it in the serializer. Adding new responsibility types requires a code change (but NOT a migration since it's stored as JSON, not a DB enum). | ✓ |
| 2 | Open strings with a recommended set — Keep a list of known values as constants but don't reject unknown ones. More flexible, but risks typos and inconsistency. | |

**User's choice:** 1
**Notes:** Decided on a strict TextChoices enum for maximum type safety and validation.

---

## Permission Enforcement Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Custom DRF Permission Class — Create a `HasResponsibility(responsibility)` permission class that hooks into `has_permission()` and `has_object_permission()`. This is the standard DRF way and keeps view code clean. | ✓ |
| 2 | Inline checks in the ViewSet — Keep a generic `IsOrganizerOrCoordinator` permission class, then check `has_responsibility` inside the `create()`, `update()`, etc. methods. | |

**User's choice:** 1
**Notes:** Opted for the cleaner, reusable DRF Permission Class architecture.

---

## Coordinator API Surface

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Shared endpoints — Use the existing `/api/organizer/...` endpoints for both organizers and coordinators. We'd update the permission classes to check if the user is *either* the organizer *or* a coordinator with the right responsibility. Keeps code very DRY. | ✓ |
| 2 | Separate endpoints — Create a new `/api/coordinator/hackathons/{hackathon_pk}/problem-statements/` endpoint suite. Keeps namespaces clean but duplicates logic. | |

**User's choice:** 1
**Notes:** We will share the organizer endpoints and use the new permission classes to gate access.

---

## Dashboard Data Contract

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Basic list: Just the hackathon details and their assigned responsibilities list. | |
| 2 | Rich list with summaries: Include high-level counts for their responsibilities so they don't have to make extra API calls immediately. (e.g. `{"stats": {"problem_statements_count": 3}}`) | ✓ |

**User's choice:** 2
**Notes:** Decided on a rich API response that includes statistics to minimize client round-trips.

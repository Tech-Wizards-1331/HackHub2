# Roadmap: Syntra

## Overview

Syntra's current milestone focuses on the Problem Statement feature for hackathon organizers.

## Phases

- [x] **Phase 1: Problem Statements** - CRUD API for hackathon problem statements with PDF uploads.

## Phase Details

### Phase 1: Problem Statements
**Goal**: Allow Organizers to create, view, update, and delete problem statements for their hackathons, with optional PDF uploads.
**Depends on**: Nothing (Hackathon and OrganizerProfile models already exist)
**Requirements**: HACK-04
**Success Criteria**:
  1. Organizers can CRUD problem statements scoped to their own hackathons.
  2. PDF file uploads are validated (only .pdf allowed).
  3. Problem statements have an is_active toggle.
  4. Non-owners cannot access another organizer's problem statements.
**Plans**: 1 plan (API implementation)

Plans:
- [x] 01-01: ProblemStatement model, serializer, viewset, and URL routing.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Problem Statements | 1/1 | Done | 2026-04-30 |
| 2. Problem Statement Selection Limits | 1/1 | Done | 2026-04-30 |
| 3. Caching for Reads | 1/1 | Done | 2026-05-02 |
| 4. Seating Allocation System | 1/1 | Done | 2026-05-02 |
| 5. Organizer Page & Demo Account | 1/1 | Done | 2026-05-02 |
| 6. Organizer Create Hackathon | 1/1 | Done | 2026-05-05 |
| 7. Seating & Problem Statement Management in Organizer | 1/1 | Done | 2026-05-05 |
| 8. Room Configuration UI | 1/1 | Done | 2026-05-05 |

### Phase 2: Problem Statement Selection Limits and Concurrency Control

**Goal:** Implement capacity constraints and ensure data integrity during participant selection.
**Requirements**: HACK-05
**Depends on:** Phase 1
**Plans:** 4 plans

Plans:
- [x] Add capacity field to ProblemStatement model
- [x] Implement thread-safe selection API with row-level locking
- [x] Enforce immutable selection (once selected, cannot change)
- [x] Verify capacity limits under concurrent selection logic

### Phase 3: Caching for Reads and Database for Writes properly, you follow a pattern called Cache Invalidation.

**Goal:** Implement Cache-Aside for problem statements and cache invalidation.
**Requirements**: TBD
**Depends on:** Phase 2
**Plans:** 1 plans

Plans:
- [x] 03-PLAN.md: Redis setup, Read-Only serializer, Cache-Aside ViewSet, Invalidation on selection.

### Phase 4: integrate seating allocation system into the organizer app

**Goal:** Integrate the python seating allocation system into the organizer API.
**Requirements**: TBD
**Depends on:** Phase 3
**Plans:** 1 plans

Plans:
- [x] 04-PLAN.md: Models, Services, API Views, URLs

### Phase 5: create orgniser page and create one demo account org@gmail.com Admin@123

**Goal:** Create organizer dashboard and demo account
**Requirements**: TBD
**Depends on:** Phase 4
**Plans:** 1 plans

Plans:
- [x] 05-PLAN.md: Management command and Template View

### Phase 6: Organizer Create Hackathon

**Goal:** Allow organizers to create new hackathons from the dashboard UI.
**Requirements**: TBD
**Depends on:** Phase 5
**Plans:** 1 plan

Plans:
- [x] 06-PLAN.md: Form, View, Template, URL

### Phase 7: Connect Seating Arrangement and Problem Statement Management in Organizer

**Goal:** Expose seating allocation and problem statement CRUD in the organizer UI.
**Requirements**: TBD
**Depends on:** Phase 6
**Plans:** 1 plan

Plans:
- [x] 07-PLAN.md: Detail page, Problem Statement CRUD, Seating UI, URLs

### Phase 8: Room Configuration UI

**Goal:** Replace the raw JSON textarea with a proper structured UI for room configuration.
**Requirements**: TBD
**Depends on:** Phase 7
**Plans:** 1 plan

Plans:
- [x] 08-PLAN.md: Dynamic JS room builder, backend cleanup

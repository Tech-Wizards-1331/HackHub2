# Syntra

## What This Is

Syntra is a hackathon management platform that handles the full lifecycle of hackathon events — from creation and team formation through submissions, judging, and logistics (attendance, food distribution). Built with Django, it serves organizers, participants, judges, and administrators through a modular, domain-driven backend.

## Core Value

A complete, production-ready Django model layer that accurately represents the full hackathon management domain — users, hackathons, teams, submissions, judging, notifications, and operations — with proper relationships, constraints, and scalable patterns.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Custom User model with email-based authentication — existing (`backend/accounts/models.py`)
- ✓ Google OAuth login via django-allauth — existing
- ✓ GitHub OAuth login via django-allauth — existing
- ✓ JWT-based REST API authentication — existing (`backend/accounts/api_views.py`)
- ✓ User flow middleware (role selection → profile completion) — existing
- ✓ Role-based access control decorator — existing (`backend/accounts/decorators.py`)

### Active

<!-- Current scope. Building toward these. -->

- [ ] Custom User model (email-based auth, admin as global role)
- [ ] UserProfile model (separate, flexible, skills optional)
- [ ] Hackathon model with status, team size constraints, soft delete
- [ ] UserRole model for per-hackathon roles (participant, judge, organizer)
- [ ] Topic model (hackathon-scoped problem statements)
- [ ] Team model with soft delete
- [ ] TeamMember model with leader/member roles and one-team-per-hackathon constraint
- [ ] TeamTopic model (one topic per team)
- [ ] TeamInvite model with invite status tracking
- [ ] Submission model with status tracking and soft delete
- [ ] Judge model (hackathon-scoped judge profiles)
- [ ] JudgeAssignment model (judge-to-submission mapping)
- [ ] EvaluationCriteria model (per-hackathon scoring rubrics)
- [ ] Score model with per-criteria scoring and feedback
- [ ] NotificationCampaign model (bulk notification creation)
- [ ] Notification model (per-user delivery tracking)
- [ ] QRCode model (team-based, hackathon-scoped)
- [ ] Attendance model (one-time team check-in)
- [ ] FoodEvent model (hackathon meal scheduling)
- [ ] FoodDistribution model (team-based meal tracking)
- [ ] Proper database indexes on high-query columns
- [ ] Soft delete pattern on hackathons, teams, submissions
- [ ] All models use appropriate timestamps (created_at, updated_at)
- [ ] All constraints (unique, FK, composite PK) accurately modeled

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Serializers — Models only for this milestone
- Views and API endpoints — Models only for this milestone
- Frontend templates — Will be addressed in a future milestone
- Email/notification delivery backend — Only the data models, not the send logic
- File upload / media storage — Not in schema
- Payment / billing — Not in schema
- Real-time features (WebSocket) — Future milestone

## Context

- **Existing codebase:** Django 6.0.3 monolith with custom User model, allauth social auth, DRF + JWT
- **Current state:** Auth system works, but all domain models are empty (no hackathons, teams, etc.)
- **Schema source:** User-designed database schema covering 20+ tables across 8 domains
- **Target apps:** accounts, hackathons, participants, submissions, judging, operations, notifications, core
- **Database:** SQLite for development (PostgreSQL planned for production)

## Constraints

- **Schema fidelity**: Do NOT change the business logic or relationships from the provided schema
- **Tech stack**: Django 6.0.3, Python
- **Auth model**: Must use existing custom User model pattern (email-based, AbstractUser)
- **Role architecture**: Admin = global role on User model; participant/judge/organizer = per-hackathon via UserRole
- **App modularity**: Models grouped by domain, not by user role

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Domain-based app structure over role-based | Current role-based apps (participant/, judge/, etc.) are empty shells. Domain-based (hackathons/, submissions/, judging/) better maps to the schema | — Pending |
| Admin as global role, others per-hackathon | Admin is platform-wide; participant/judge/organizer roles are hackathon-specific | — Pending |
| Soft delete via `deleted_at` field | Preserve data for audit/recovery on hackathons, teams, submissions | — Pending |
| TextChoices for all enums | Django-native, no external enum dependency, DB-portable | — Pending |
| Separate UserProfile model | Keep User model lean; profile data (skills, bio) is optional and extensible | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-17 after initialization*

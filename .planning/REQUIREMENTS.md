# Requirements: Syntra

**Defined:** 2026-04-17
**Core Value:** A complete, production-ready Django model layer for hackathon management

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Accounts

- [ ] **AUTH-01**: Custom User model with email-based auth (AbstractUser, no username, email as USERNAME_FIELD)
- [ ] **AUTH-02**: User model includes Django auth fields (is_active, is_staff, is_superuser) via AbstractUser
- [ ] **AUTH-03**: Custom UserManager for email-based create_user/create_superuser
- [ ] **AUTH-04**: UserProfile model as OneToOneField with User (name, skills, bio — all optional/flexible)

### Hackathons

- [ ] **HACK-01**: Hackathon model with title, description, organizer FK, dates, status enum, team size constraints, soft delete
- [ ] **HACK-02**: Hackathon date validation (start_date < end_date, registration_deadline <= start_date)
- [ ] **HACK-03**: Hackathon team size validation (min_team_size <= max_team_size, both > 0)
- [ ] **HACK-04**: UserRole model with per-hackathon roles (participant, judge, organizer), composite unique (user, hackathon, role)
- [ ] **HACK-05**: Topic model with hackathon FK, title, description, max_teams_allowed

### Participants

- [ ] **PART-01**: Team model with hackathon FK, name, timestamps, soft delete
- [ ] **PART-02**: TeamMember model with team role enum (leader/member), joined_at timestamp
- [ ] **PART-03**: TeamMember unique constraint: one team per user per hackathon (user_id, hackathon_id)
- [ ] **PART-04**: TeamMember team size enforcement via model clean() validation against hackathon max_team_size
- [ ] **PART-05**: TeamTopic model as OneToOneField on team (one topic per team), with topic FK
- [ ] **PART-06**: TeamInvite model with invite status enum (pending/accepted/rejected/expired), unique (team_id, invited_user_id)

### Submissions

- [ ] **SUBM-01**: Submission model with team FK, title, description, github_url, status enum, soft delete
- [ ] **SUBM-02**: Submission uniqueness: one submission per team (unique constraint on team_id)

### Judging

- [ ] **JUDG-01**: Judge model (user FK + hackathon FK, max_teams_allowed), unique (user_id, hackathon_id)
- [ ] **JUDG-02**: JudgeAssignment model (judge FK + submission FK), unique pair
- [ ] **JUDG-03**: EvaluationCriteria model (hackathon FK, name, max_score as float)
- [ ] **JUDG-04**: Score model with submission FK, judge FK, criteria FK, score float, feedback text
- [ ] **JUDG-05**: Score unique constraint: (submission_id, judge_id, criteria_id)
- [ ] **JUDG-06**: Score validation: score must not exceed criteria max_score (clean() validation)

### Operations

- [ ] **OPER-01**: QRCode model (team FK, hackathon FK, unique code text, expires_at timestamp)
- [ ] **OPER-02**: QRCode unique constraint: one QR per team per hackathon
- [ ] **OPER-03**: QRCode expiry safety: is_expired property/method for runtime checks
- [ ] **OPER-04**: Attendance model (team FK, hackathon FK, members_present_count, scanned_at)
- [ ] **OPER-05**: Attendance unique constraint: one check-in per team per hackathon
- [ ] **OPER-06**: FoodEvent model (hackathon FK, name, start_time, end_time)
- [ ] **OPER-07**: FoodDistribution model (food_event FK, team FK, members_served_count, scanned_at)

### Notifications

- [ ] **NOTF-01**: NotificationCampaign model (hackathon FK, title, message, created_by FK, target_audience enum)
- [ ] **NOTF-02**: Target audience enum clearly defined: all_participants, all_judges, all_organizers, all_teams, specific_team
- [ ] **NOTF-03**: Notification model (user FK, campaign FK, is_read boolean, delivered_at, created_at)

### Core

- [ ] **CORE-01**: TimestampedModel abstract base class (created_at with auto_now_add, updated_at with auto_now)
- [ ] **CORE-02**: SoftDeleteModel abstract base class (deleted_at nullable, custom manager to filter soft-deleted)
- [ ] **CORE-03**: Database indexes: team_members(user_id), submissions(team_id), scores(submission_id), judge_assignments(judge_id), notifications(user_id), food_distribution(team_id, food_event_id)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### API Layer

- **API-01**: REST API endpoints for all models (DRF serializers + viewsets)
- **API-02**: Permission classes for role-based API access
- **API-03**: Pagination, filtering, and search on list endpoints

### Frontend

- **FE-01**: Dashboard templates for each role
- **FE-02**: Team management UI (create, invite, accept/reject)
- **FE-03**: Submission upload and review interface
- **FE-04**: Judging scorecard interface

### Infrastructure

- **INFRA-01**: PostgreSQL database configuration
- **INFRA-02**: Redis caching layer
- **INFRA-03**: Celery task queue for async operations
- **INFRA-04**: Email notification delivery backend

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Serializers, views, API logic | Models-only milestone |
| Frontend templates | Future milestone |
| Email/notification delivery | Only data models, not send logic |
| File upload / media storage | Not in schema |
| Payment / billing | Not in schema |
| Real-time features (WebSocket) | Future milestone |
| Docker / deployment config | Infrastructure milestone |
| Test suite | Separate phase |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | — | Pending |
| AUTH-02 | — | Pending |
| AUTH-03 | — | Pending |
| AUTH-04 | — | Pending |
| HACK-01 | — | Pending |
| HACK-02 | — | Pending |
| HACK-03 | — | Pending |
| HACK-04 | — | Pending |
| HACK-05 | — | Pending |
| PART-01 | — | Pending |
| PART-02 | — | Pending |
| PART-03 | — | Pending |
| PART-04 | — | Pending |
| PART-05 | — | Pending |
| PART-06 | — | Pending |
| SUBM-01 | — | Pending |
| SUBM-02 | — | Pending |
| JUDG-01 | — | Pending |
| JUDG-02 | — | Pending |
| JUDG-03 | — | Pending |
| JUDG-04 | — | Pending |
| JUDG-05 | — | Pending |
| JUDG-06 | — | Pending |
| OPER-01 | — | Pending |
| OPER-02 | — | Pending |
| OPER-03 | — | Pending |
| OPER-04 | — | Pending |
| OPER-05 | — | Pending |
| OPER-06 | — | Pending |
| OPER-07 | — | Pending |
| NOTF-01 | — | Pending |
| NOTF-02 | — | Pending |
| NOTF-03 | — | Pending |
| CORE-01 | — | Pending |
| CORE-02 | — | Pending |
| CORE-03 | — | Pending |

**Coverage:**
- v1 requirements: 36 total
- Mapped to phases: 0
- Unmapped: 36 ⚠️

---
*Requirements defined: 2026-04-17*
*Last updated: 2026-04-17 after initial definition*

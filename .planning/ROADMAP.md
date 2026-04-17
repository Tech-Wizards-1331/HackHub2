# Roadmap: Syntra v1.0

**Created:** 2026-04-17
**Granularity:** Coarse (3–5 phases)
**Total requirements:** 36

## Milestone: v1.0 — Production-Ready Django Models

### Phase 1: Core Foundation & User Models

**Goal:** Establish abstract base classes and the accounts app with User + UserProfile models.

**Requirements:** CORE-01, CORE-02, AUTH-01, AUTH-02, AUTH-03, AUTH-04

**UI hint**: no

**Success criteria:**
1. TimestampedModel abstract base provides created_at/updated_at to all child models
2. SoftDeleteModel abstract base provides deleted_at field with custom manager filtering
3. Custom User model uses email as USERNAME_FIELD with no username field
4. User model includes is_active, is_staff, is_superuser via AbstractUser
5. UserProfile exists as OneToOneField linked to User with optional fields
6. `python manage.py makemigrations` succeeds for core and accounts apps

**Depends on:** Nothing

---

### Phase 2: Hackathons, Roles & Team Formation

**Goal:** Build hackathon management, per-hackathon user roles, topics, teams, team members, team topics, and invites.

**Requirements:** HACK-01, HACK-02, HACK-03, HACK-04, HACK-05, PART-01, PART-02, PART-03, PART-04, PART-05, PART-06

**UI hint**: no

**Success criteria:**
1. Hackathon model with status choices, soft delete, and date/team-size validation in clean()
2. UserRole model with composite unique constraint (user, hackathon, role)
3. Topic model scoped to hackathon with max_teams_allowed
4. Team model with hackathon FK and soft delete
5. TeamMember enforces one-team-per-hackathon unique constraint and team size limit via clean()
6. TeamTopic is OneToOne on team_id with topic FK
7. TeamInvite has status enum and unique (team, invited_user)
8. `python manage.py makemigrations` succeeds for hackathons and participants apps

**Depends on:** Phase 1

---

### Phase 3: Submissions & Judging System

**Goal:** Build submission tracking with one-per-team uniqueness, judge assignments, evaluation criteria, and score validation.

**Requirements:** SUBM-01, SUBM-02, JUDG-01, JUDG-02, JUDG-03, JUDG-04, JUDG-05, JUDG-06

**UI hint**: no

**Success criteria:**
1. Submission model with team FK (unique), status enum, and soft delete
2. Judge model scoped to hackathon with max_teams_allowed and unique (user, hackathon)
3. JudgeAssignment links judge to submission with unique pair constraint
4. EvaluationCriteria defines per-hackathon scoring rubrics with max_score
5. Score model has unique (submission, judge, criteria) and clean() validates score <= max_score
6. `python manage.py makemigrations` succeeds for submissions and judging apps

**Depends on:** Phase 2

---

### Phase 4: Operations, Notifications & Indexes

**Goal:** Build QR codes, attendance, food distribution, notification campaigns, per-user notifications, and database indexes.

**Requirements:** OPER-01, OPER-02, OPER-03, OPER-04, OPER-05, OPER-06, OPER-07, NOTF-01, NOTF-02, NOTF-03, CORE-03

**UI hint**: no

**Success criteria:**
1. QRCode model with unique code, expiry, unique (team, hackathon), and is_expired property
2. Attendance model with unique (team, hackathon) for one-time check-in
3. FoodEvent model for hackathon meal scheduling
4. FoodDistribution model for team-based meal tracking
5. NotificationCampaign with clearly defined target_audience enum (all_participants, all_judges, etc.)
6. Notification model with per-user delivery tracking (is_read, delivered_at)
7. All database indexes from schema applied via Meta.indexes
8. `python manage.py makemigrations && python manage.py migrate` succeeds for full project

**Depends on:** Phase 3

---

## Phase Summary

| # | Phase | Requirements | Count |
|---|-------|-------------|-------|
| 1 | Core Foundation & User Models | CORE-01, CORE-02, AUTH-01–04 | 6 |
| 2 | Hackathons, Roles & Team Formation | HACK-01–05, PART-01–06 | 11 |
| 3 | Submissions & Judging System | SUBM-01–02, JUDG-01–06 | 8 |
| 4 | Operations, Notifications & Indexes | OPER-01–07, NOTF-01–03, CORE-03 | 11 |
| **Total** | | | **36** |

## Coverage

- v1 requirements: 36
- Mapped to phases: 36
- Unmapped: 0 ✓

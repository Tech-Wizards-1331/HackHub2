---
phase: 1
slug: setup-coordinator-app
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Django Test (unittest) |
| **Config file** | `backend/syntra/settings.py` |
| **Quick run command** | `python manage.py test coordinator` |
| **Full suite command** | `python manage.py test` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python manage.py check` or `python manage.py makemigrations --dry-run`
- **After every plan wave:** Run `python manage.py test coordinator`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | COORD-01 | — | N/A | config | `python manage.py check` | ✅ | ⬜ pending |
| 1-01-02 | 01 | 1 | COORD-02 | — | N/A | migration | `python manage.py makemigrations --dry-run` | ✅ | ⬜ pending |
| 1-01-03 | 01 | 2 | COORD-03 | — | N/A | unit | `python manage.py test coordinator` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/coordinator/tests.py` — stubs for Phase 1 tests

*Existing infrastructure covers the rest.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard visualization | COORD-03 | UI interaction | Test via API client to verify JSON structure matches CONTEXT.md |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-22

---
wave: 1
depends_on: []
files_modified:
  - backend/requirements.txt
  - backend/participant/models.py
  - backend/organizer/models.py
  - backend/organizer/permissions.py
  - backend/organizer/api_serializers.py
  - backend/organizer/api_views.py
  - backend/organizer/api_urls.py
  - backend/organizer/tests_scanner.py
autonomous: true
---

# Phase 11: Build a production-ready real-time QR scanner system for Syntra hackathons using a “One QR per Team” architecture - Plan

## Verification Criteria
- [ ] `qrcode` package added to `requirements.txt`.
- [ ] `Team` model has `qr_token` field and automatically generates the QR code on save.
- [ ] `HackathonCoordinator`, `ScanCategory`, and `ScanRecord` models added to organizer app.
- [ ] Database migrations created and applied.
- [ ] Custom `IsScannerAuthorized` permission class implemented.
- [ ] `/api/organizer/scanner/scan/` and `/api/organizer/scanner/submit/` APIs functioning.
- [ ] API is secured and prevents unauthorized access (participants/anonymous).
- [ ] Tests created in `tests_scanner.py` pass cleanly.

## Must Haves
- Live, real-time database updates and API responses.
- One QR code containing only the unique token per team.
- Scoped coordinator authorization checks.
- DB level unique constraints to prevent double scanning.
- Transaction safety during scanner submissions.

## Tasks

```xml
<task>
  <id>update-requirements</id>
  <description>Add qrcode dependency to requirements.txt</description>
  <read_first>
    - backend/requirements.txt
  </read_first>
  <action>
    Modify backend/requirements.txt to add qrcode package.
  </action>
  <acceptance_criteria>
    - `grep "qrcode" backend/requirements.txt` exits 0.
  </acceptance_criteria>
</task>

<task>
  <id>update-models</id>
  <description>Add qr_token to Team model and create coordinator, scan category, and scan record models</description>
  <read_first>
    - backend/participant/models.py
    - backend/organizer/models.py
  </read_first>
  <action>
    Modify backend/participant/models.py:
    - Add `qr_token` UUID field to Team.
    - Override `save()` to generate the QR image containing only the `qr_token` when saved.

    Modify backend/organizer/models.py:
    - Add `HackathonCoordinator` model with fields `hackathon`, `user`, `is_active`, `created_at`.
    - Add `ScanCategory` model with fields `hackathon`, `name`, `is_active`, `display_order`, `created_at`.
    - Add `ScanRecord` model with fields `team_member`, `scan_category`, `scanned_by`, `created_at`.
  </action>
  <acceptance_criteria>
    - `HackathonCoordinator` model is defined.
    - `ScanCategory` model is defined.
    - `ScanRecord` model is defined.
    - `Team` model generates QR code.
  </acceptance_criteria>
</task>

<task>
  <id>makemigrations-migrate</id>
  <description>Generate and apply migrations</description>
  <read_first>
    - backend/manage.py
  </read_first>
  <action>
    Run `python manage.py makemigrations` and `python manage.py migrate` in the `backend` directory to apply the model changes.
  </action>
  <acceptance_criteria>
    - Migrations apply successfully.
  </acceptance_criteria>
</task>

<task>
  <id>implement-permissions</id>
  <description>Create custom permission IsScannerAuthorized for hackathon scanner API access</description>
  <read_first>
    - backend/organizer/models.py
  </read_first>
  <action>
    Create backend/organizer/permissions.py:
    - Implement `IsScannerAuthorized` class that checks if a user is an organizer (owner) or an active coordinator for the hackathon context.
  </action>
  <acceptance_criteria>
    - Permissions class correctly validates authorization.
  </acceptance_criteria>
</task>

<task>
  <id>implement-views-serializers</id>
  <description>Create scanner serializers and views, register URL paths</description>
  <read_first>
    - backend/organizer/api_views.py
    - backend/organizer/api_serializers.py
    - backend/organizer/api_urls.py
  </read_first>
  <action>
    Add serializers to backend/organizer/api_serializers.py.
    Add ScannerScanView and ScannerSubmitView to backend/organizer/api_views.py.
    Register routes in backend/organizer/api_urls.py.
  </action>
  <acceptance_criteria>
    - Views process scan/submit correctly.
  </acceptance_criteria>
</task>

<task>
  <id>create-tests</id>
  <description>Write scanner tests and run test suite</description>
  <read_first>
    - backend/organizer/api_views.py
  </read_first>
  <action>
    Create backend/organizer/tests_scanner.py with full test cases.
    Run tests using `python manage.py test organizer.tests_scanner`.
  </action>
  <acceptance_criteria>
    - Tests pass.
  </acceptance_criteria>
</task>
```

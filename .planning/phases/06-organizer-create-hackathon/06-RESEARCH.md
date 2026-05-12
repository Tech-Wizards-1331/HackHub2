# Phase 6 Research: Organizer Create Hackathon

## Codebase Scout

### Existing Assets
- **Model:** `Hackathon` in `backend/organizer/models.py` (lines 18-43) — all fields already defined.
- **Dashboard View:** `OrganizerDashboardView` in `backend/organizer/views.py` — uses `LoginRequiredMixin` + `UserPassesTestMixin` pattern.
- **Dashboard Template:** `backend/organizer/templates/organizer/dashboard.html` — clean HTML, styled inline.
- **URL Config:** `backend/organizer/urls.py` — single route currently, easily extensible.
- **OrganizerProfile:** linked to User via OneToOneField, referenced as `request.user.organizer_profile`.

### Hackathon Model Fields for Form
| Field | Type | Required | Default | Include in Form |
|-------|------|----------|---------|-----------------|
| name | CharField(255) | Yes | — | ✅ |
| description | TextField | No | null | ✅ |
| start_date | DateTimeField | Yes | — | ✅ |
| end_date | DateTimeField | Yes | — | ✅ |
| registration_deadline | DateTimeField | Yes | — | ✅ |
| min_team_size | PositiveIntegerField | Yes | 1 | ✅ |
| max_team_size | PositiveIntegerField | Yes | 4 | ✅ |
| status | CharField | Yes | 'registration_open' | ❌ (auto-set) |
| organizer | FK(OrganizerProfile) | Yes | — | ❌ (auto-set from user) |
| room_configuration | JSONField | No | null | ❌ (later) |
| seating_allocation | JSONField | No | null | ❌ (later) |

### Pattern to Follow
The existing `OrganizerDashboardView` uses class-based views with `LoginRequiredMixin` + `UserPassesTestMixin`. The new `CreateHackathonView` should follow the same mixin pattern but use Django's `CreateView` instead of `TemplateView`.

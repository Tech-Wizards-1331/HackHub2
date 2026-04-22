# Phase 1: Setup Coordinator App - Research

**Researched:** 2026-04-22
**Phase:** 01-setup-coordinator-app
**Requirements:** COORD-01, COORD-02, COORD-03

## Codebase Architecture Analysis

### Existing App Structure Pattern

Every role-based app in the project follows the same file structure:

```
backend/{app_name}/
├── __init__.py
├── admin.py           # Django admin registration
├── api_serializers.py  # DRF serializers
├── api_urls.py         # DRF router + URL patterns
├── api_views.py        # DRF ViewSets / APIViews
├── apps.py             # AppConfig
├── models.py           # Django models
├── urls.py             # Template-based URL patterns
├── views.py            # Template-based views
├── migrations/
└── tests.py
```

The `coordinator` app MUST follow this exact structure for consistency.

### Authentication & Permission Patterns

**JWT Authentication (API):**
- All DRF views use `authentication_classes = [JWTAuthentication]`
- `rest_framework_simplejwt` is the JWT library (v5.5.1)
- Global DRF defaults in settings: `JWTAuthentication` + `IsAuthenticated`

**Role-based API permissions:**
- Pattern: Custom `BasePermission` subclass per role
- Example from `organizer/api_views.py`:
  ```python
  class IsOrganizer(permissions.BasePermission):
      def has_permission(self, request, view):
          return bool(request.user and request.user.is_authenticated 
                      and request.user.role == User.Role.ORGANIZER)
  ```
- Applied as `permission_classes = [IsOrganizer]` on ViewSets

**Template-based views:**
- Use `@role_required('organizer')` decorator from `accounts/decorators.py`
- Decorator checks `request.user.role` and returns 403 if no match
- Superusers bypass role checks

### User Model & Role System

**Existing roles** (defined as `TextChoices` on `User` model):
- `participant`, `organizer`, `judge`, `volunteer`, `super_admin`, `coordinator`

**Key finding:** `COORDINATOR` is already in `User.Role.COORDINATOR`. No migration needed for the role choice itself.

**Role is a single CharField** (`max_length=20`). A user can only have ONE global role. This means if a user is promoted to `coordinator`, they lose their previous role.

### HackathonCoordinator Model (Already Exists)

Located in `organizer/models.py`:
```python
class HackathonCoordinator(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='coordinated_hackathons')
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, 
                                  related_name='coordinators')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hackathon')
```

**What needs to be added:** A `responsibilities` field (JSONField) per CONTEXT.md decision D-06.

### Existing assign_coordinator Action

Located in `organizer/api_views.py` on `HackathonViewSet`:
- Accepts `email` in POST body
- Looks up user, sets `user.role = COORDINATOR` if not already
- Creates `HackathonCoordinator` link
- **Currently does NOT handle `responsibilities`** — needs update after field is added

### URL Routing Patterns

**Top-level (`syntra/urls.py`):**
- Template views: `path('organizer/', include('organizer.urls'))`
- API: via `api/urls.py` → `path('api/auth/', include('accounts.api_urls'))`

**API routing (`api/urls.py`):**
```python
urlpatterns = [
    path('hello/', hello_api, name='hello_api'),
    path('organizer/', include('organizer.api_urls')),
]
```

**Coordinator app should add:**
- `path('coordinator/', include('coordinator.api_urls'))` in `api/urls.py`
- `path('coordinator/', include('coordinator.urls'))` in `syntra/urls.py` (for template views)

### Serializer Patterns

- `ModelSerializer` with `Meta.fields` and `Meta.read_only_fields`
- Computed fields via `SerializerMethodField` (e.g., `pdf_file_url`)
- Cross-model lookups: `serializers.EmailField(source='user.email', read_only=True)`

### Admin Registration Pattern

```python
@admin.register(ModelClass)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2')
    search_fields = ('field1', 'related__field')
```

## Technical Decisions

### JSONField for Responsibilities

Django's built-in `models.JSONField` works with SQLite (Django 4.2+). Since project uses Django 6.0.3 and SQLite, `JSONField` is fully supported. No extra dependencies needed.

**Schema for responsibilities:**
```python
responsibilities = models.JSONField(
    default=list,
    blank=True,
    help_text='Assigned responsibilities: problem_statements, teams, analytics'
)
```

**Valid values:** `["problem_statements"]`, `["teams", "analytics"]`, `["problem_statements", "teams", "analytics"]`

### Team Model — Does NOT Exist Yet

**Critical finding:** There is NO `Team` model anywhere in the codebase. The `participant` app has `ParticipantProfile` and `Skill` but no teams. The `Hackathon.max_team_size` and `Hackathon.max_teams` fields exist but there's no `Team` model to reference.

**Impact on coordinator capabilities:**
- Team Manager responsibility (`teams`) will need to work with whatever team model exists (or will exist in future)
- For Phase 1, Team Manager capabilities should be limited to reading team-related counts from the hackathon (which currently would be 0)
- The actual Team model should be created in a future phase

### Dashboard Endpoint Design

Based on CONTEXT.md decisions, the dashboard should be a single `GET /api/coordinator/dashboard/` endpoint that returns:

```json
{
  "hackathons": [
    {
      "id": 1,
      "name": "HackSprint 2026",
      "status": "published",
      "registration_status": "open",
      "responsibilities": ["problem_statements", "analytics"],
      "summary": {
        "problem_statements": { "total": 5, "active": 3 },
        "analytics": { "total_teams": 0, "total_participants": 0 }
      }
    }
  ]
}
```

The `summary` field only includes counts for the coordinator's assigned responsibilities.

### Three-Layer Permission Implementation

```
Layer 1: IsCoordinator (BasePermission.has_permission)
  → Checks user.role == COORDINATOR

Layer 2: IsAssignedToHackathon (BasePermission.has_object_permission)
  → Checks HackathonCoordinator.objects.filter(user=user, hackathon=obj).exists()

Layer 3: HasResponsibility (custom check)
  → Checks "problem_statements" in coordinator_assignment.responsibilities
```

Options for Layer 3 implementation:
1. **Separate permission class** — `HasResponsibility('problem_statements')` as a parameterized permission
2. **Mixin method** — `check_responsibility(request, hackathon, 'problem_statements')` utility
3. **Combined in Layer 2** — Single permission class with both hackathon + responsibility check

**Recommendation:** Option 2 (mixin/utility) — most flexible, keeps permissions composable, follows DRF conventions. A single `IsCoordinator` permission handles Layer 1, and a `CoordinatorPermissionMixin` on ViewSets handles Layers 2+3 in `get_queryset()` and a utility method.

## Risk Assessment

### Low Risk
- Creating the coordinator app (standard Django `startapp` + file creation)
- CoordinatorProfile model (simple OneToOne FK pattern already in codebase)
- Admin registration (well-established pattern)
- URL routing (documented pattern in codebase)

### Medium Risk
- Adding `responsibilities` JSONField to `HackathonCoordinator` — requires migration on existing model in organizer app
- Updating `assign_coordinator` action to accept responsibilities — modifies existing working endpoint
- Dashboard endpoint aggregation queries — multiple queries to build summary counts

### Low Risk but Important
- Team-related features — No `Team` model exists yet. Team Manager role should return zero counts gracefully, not error.

## Validation Architecture

### Testable Assertions
1. `coordinator` app appears in `INSTALLED_APPS` and `python manage.py check` passes
2. `CoordinatorProfile` can be created for a user with `role=COORDINATOR`
3. `GET /api/coordinator/dashboard/` returns HTTP 200 with JWT for coordinator user
4. `GET /api/coordinator/dashboard/` returns HTTP 403 for non-coordinator users
5. Dashboard response includes only hackathons the coordinator is assigned to
6. Dashboard `summary` only includes data for assigned responsibilities
7. `HackathonCoordinator.responsibilities` field accepts JSON arrays
8. Problem statement endpoints enforce responsibility check

## RESEARCH COMPLETE

---
wave: 1
depends_on: []
files_modified:
  - backend/requirements.txt
  - backend/syntra/settings.py
  - backend/organizer/api_serializers.py
  - backend/participant/api_serializers.py
  - backend/participant/api_views.py
  - backend/participant/api_urls.py
autonomous: true
must_haves:
  - Django Cache backend is configured with Redis and fallback LocMemCache
  - A Participant Read-Only endpoint returns cached problem statements
  - Cache is invalidated when a team selects a problem statement
---

# Phase 3: Caching for Reads and Database for Writes

This plan implements a Cache-Aside architecture for reading problem statements and Write-Through invalidation when a team selects a problem statement, ensuring sub-millisecond read times for participants while maintaining strict data integrity.

## Tasks

### 1. Install and Configure Redis
Configure Django to use Redis as the caching backend via `django-redis`.

<read_first>
- backend/syntra/settings.py
</read_first>
<action>
1. Add `django-redis==5.4.0` to `backend/requirements.txt` under a new `# Caching` header.
2. In `backend/syntra/settings.py`, add the `CACHES` configuration block.
3. Configure the `default` cache to use `django_redis.cache.RedisCache` if the `REDIS_URL` environment variable is set.
4. Fall back to `django.core.cache.backends.locmem.LocMemCache` if `REDIS_URL` is missing (ensuring local development works out of the box without requiring a local Redis server).
</action>
<acceptance_criteria>
- `backend/requirements.txt` contains `django-redis`
- `backend/syntra/settings.py` contains `CACHES = {` and references `REDIS_URL`
- `backend/syntra/settings.py` contains fallback to `LocMemCache`
</acceptance_criteria>

### 2. Update Organizer Serializer
Fix the missing `max_teams_allowed` field in the Organizer's problem statement serializer from Phase 2.

<read_first>
- backend/organizer/api_serializers.py
- backend/organizer/models.py
</read_first>
<action>
1. Edit `ProblemStatementSerializer` in `backend/organizer/api_serializers.py`.
2. Add `'max_teams_allowed'` to the `fields` list.
</action>
<acceptance_criteria>
- `backend/organizer/api_serializers.py` contains `'max_teams_allowed'` in the `fields` array of `ProblemStatementSerializer`.
</acceptance_criteria>

### 3. Create Participant Serializer
Create a specialized Read-Only serializer for Participants that includes capacity metrics.

<read_first>
- backend/participant/api_serializers.py
</read_first>
<action>
1. In `backend/participant/api_serializers.py`, create a new serializer `ParticipantProblemStatementSerializer` that inherits from `serializers.ModelSerializer`.
2. Set the model to `organizer.models.ProblemStatement`.
3. Define two new `serializers.IntegerField` fields: `current_teams_count` (read-only) and `is_full` (a `serializers.BooleanField`, read-only).
4. The `fields` array should be: `['id', 'title', 'description', 'pdf_file', 'max_teams_allowed', 'current_teams_count', 'is_full']`.
</action>
<acceptance_criteria>
- `backend/participant/api_serializers.py` contains `class ParticipantProblemStatementSerializer(serializers.ModelSerializer):`
- The new serializer includes `current_teams_count` and `is_full` fields.
</acceptance_criteria>

### 4. Implement Cache-Aside Read Endpoint
Create the Read-Only endpoint for participants that utilizes the cache.

<read_first>
- backend/participant/api_views.py
</read_first>
<action>
1. In `backend/participant/api_views.py`, create `ParticipantProblemStatementViewSet(viewsets.ReadOnlyModelViewSet)`.
2. Set `serializer_class = ParticipantProblemStatementSerializer`.
3. Set `permission_classes = [permissions.IsAuthenticated]`.
4. Override the `list` method to implement the Cache-Aside pattern:
   - Extract `hackathon_id` from `request.query_params` (return 400 if missing).
   - Define cache key: `cache_key = f"problem_statements_list_{hackathon_id}"`
   - Attempt to fetch from cache: `cached_data = cache.get(cache_key)` (import `django.core.cache.cache`).
   - If `cached_data` exists, return `Response(cached_data)`.
   - If not in cache, fetch from DB: filter `ProblemStatement` by `hackathon_id` and `is_active=True`.
   - Annotate the queryset: `annotate(current_teams_count=Count('selected_by_teams'))` (import `django.db.models.Count`).
   - Also annotate `is_full=Case(When(current_teams_count__gte=F('max_teams_allowed'), then=Value(True)), default=Value(False), output_field=BooleanField())`.
   - Serialize the annotated queryset.
   - Cache the serialized data (`serializer.data`) using `cache.set(cache_key, serializer.data, timeout=3600)`.
   - Return `Response(serializer.data)`.
</action>
<acceptance_criteria>
- `backend/participant/api_views.py` contains `ParticipantProblemStatementViewSet`
- `backend/participant/api_views.py` imports `django.core.cache.cache`
- The `list` method checks for `cache_key` and uses `cache.set` before returning.
</acceptance_criteria>

### 5. Wire Up Participant Endpoint
Register the new endpoint in the URL router.

<read_first>
- backend/participant/api_urls.py
</read_first>
<action>
1. In `backend/participant/api_urls.py`, import `ParticipantProblemStatementViewSet`.
2. Register the viewset with the router: `router.register(r'problem-statements', ParticipantProblemStatementViewSet, basename='participant-problem-statement')`.
</action>
<acceptance_criteria>
- `backend/participant/api_urls.py` contains `router.register(r'problem-statements'`
</acceptance_criteria>

### 6. Implement Cache Invalidation (Write-Through)
Invalidate the cache precisely when a team locks in a problem statement.

<read_first>
- backend/participant/api_views.py
</read_first>
<action>
1. In `backend/participant/api_views.py`, locate the `select_problem_statement` action inside `TeamViewSet`.
2. Inside the `with transaction.atomic():` block, after successfully setting `team.selected_problem_statement = ps` and calling `team.save()`, add the cache invalidation logic.
3. Define the cache key using the team's hackathon ID: `cache_key = f"problem_statements_list_{team.hackathon.id}"`.
4. Delete the key: `cache.delete(cache_key)`.
</action>
<acceptance_criteria>
- `select_problem_statement` inside `TeamViewSet` contains `cache.delete(cache_key)` where `cache_key` matches the format `problem_statements_list_{hackathon_id}`.
</acceptance_criteria>

## Verification
- Run `python manage.py check` to ensure no syntax errors.
- Start the server and verify that hitting the participant `/api/participant/problem-statements/?hackathon_id=X` endpoint caches the response.
- Verify that calling `/api/participant/teams/Y/select_problem_statement/` clears the cache and subsequent reads reflect the updated `current_teams_count`.

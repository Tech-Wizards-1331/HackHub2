# Phase 11 Research: Real-Time QR Scanner System

## 1. Context & Architecture Overview
This phase builds a production-ready, real-time QR scanner system for Syntra hackathons. The QR scanner is used by hackathon organizers and authorized volunteers/coordinators to scan team QR codes and instantly mark selected members as scanned for specific categories.

The scanner system operates fully online with live API validation and direct database updates (no offline caching or bulk synchronization).

### Component Breakdown
1. **Models**:
   - `Team` (modified in `participant/models.py`): Add `qr_token` UUID field. Auto-generate the QR code image using the `qrcode` library on save.
   - `HackathonCoordinator` (new in `organizer/models.py`): Scoped role associating a user with a hackathon for volunteer/coordinator permissions.
   - `ScanCategory` (new in `organizer/models.py`): Dynamic database representation of scan events (e.g., Attendance, Meals, Swag).
   - `ScanRecord` (new in `organizer/models.py`): Log of individual team member scans for a specific category.

2. **Permissions**:
   - `IsScannerAuthorized` (custom permission class): Validates that the request user is either the hackathon's organizer or an active coordinator/volunteer for that hackathon.

3. **APIs**:
   - `POST /api/organizer/scanner/scan/`: Validates a scanned QR token and returns team/member scan status.
   - `POST /api/organizer/scanner/submit/`: Marks selected members as scanned by creating `ScanRecord` instances in a database transaction block.

---

## 2. Technical Details & Database Models

### Team Model Modifications
Add `qr_token` to `Team`:
```python
import uuid
qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
```
Override `save()` to auto-generate the QR code image containing only the stringified UUID:
```python
import qrcode
from io import BytesIO
from django.core.files import File

def save(self, *args, **kwargs):
    if not self.qr_code:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(self.qr_token))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"team_{self.id}_qr.png"
        self.qr_code.save(filename, File(buffer), save=False)
    super().save(*args, **kwargs)
```

### HackathonCoordinator Model
To support per-hackathon scoped permissions for volunteers/coordinators:
```python
class HackathonCoordinator(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='coordinators')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coordinated_hackathons')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hackathon', 'user')
```

### ScanCategory Model
```python
class ScanCategory(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='scan_categories')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']
        unique_together = ('hackathon', 'name')
```

### ScanRecord Model
```python
class ScanRecord(models.Model):
    team_member = models.ForeignKey('participant.TeamMember', on_delete=models.CASCADE, related_name='scan_records')
    scan_category = models.ForeignKey(ScanCategory, on_delete=models.CASCADE, related_name='scan_records')
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scanned_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team_member', 'scan_category')
```

---

## 3. Permissions Design (`IsScannerAuthorized`)
The reusable permission class will reside in `organizer/permissions.py` (or inside `api_views.py`):
```python
from rest_framework import permissions
from organizer.models import HackathonCoordinator, ScanCategory
from participant.models import Team

class IsScannerAuthorized(permissions.BasePermission):
    """
    Allows access only to the owning organizer or authorized coordinators/volunteers
    for the hackathon context of the scan.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Check global superuser
        if request.user.is_staff or request.user.role == 'super_admin':
            return True
            
        # Determine hackathon context from payload
        hackathon_id = request.data.get('hackathon_id')
        scan_category_id = request.data.get('scan_category_id')
        qr_token = request.data.get('qr_token')
        
        hackathon = None
        if qr_token:
            try:
                hackathon = Team.objects.get(qr_token=qr_token).hackathon
            except Team.DoesNotExist:
                return False
        elif scan_category_id:
            try:
                hackathon = ScanCategory.objects.get(id=scan_category_id).hackathon
            except ScanCategory.DoesNotExist:
                return False
        elif hackathon_id:
            try:
                hackathon = Hackathon.objects.get(id=hackathon_id)
            except Hackathon.DoesNotExist:
                return False
                
        if not hackathon:
            return False
            
        # 1. Check if user is the owning Organizer
        if request.user.role == 'organizer' and hackathon.organizer.user == request.user:
            return True
            
        # 2. Check if user is an active Coordinator/Volunteer for this hackathon
        is_coordinator = HackathonCoordinator.objects.filter(
            hackathon=hackathon,
            user=request.user,
            is_active=True
        ).exists()
        
        return is_coordinator
```

---

## 4. API Endpoints Logic

### 1. `/api/organizer/scanner/scan/` [POST]
Accepts `qr_token` and `scan_category_id`.
- Validates that `qr_token` corresponds to a valid `Team`.
- Fetches all team members for this team.
- Checks if a `ScanRecord` exists for each member in the selected `scan_category_id`.
- Returns lightweight JSON payload.
- Optimizes queries with `prefetch_related` or `select_related` on member scans.

### 2. `/api/organizer/scanner/submit/` [POST]
Accepts `scan_category_id`, `qr_token`, and list of `member_ids`.
- Validates scanner authorization.
- Verifies that all `member_ids` belong to the team associated with the `qr_token`.
- Uses a synchronous database transaction block to prevent partial updates.
- Creates `ScanRecord` instances for selected members.
- Validates and prevents double-scanning.

---

## 5. Verification Strategy & Test Cases
Since tests run under SQLite locally, we can run them instantly.
Test suite will verify:
1. **Duplicate Prevention**: Assert database integrity checks prevent multiple `ScanRecord` rows for the same `(team_member, scan_category)`.
2. **Access Control**: Verify participant or unauthenticated users get 403 Forbidden on scan/submit endpoints.
3. **Invalid Token**: Verify HTTP 404/400 returned on unknown QR token.
4. **Member Validation**: Verify a volunteer cannot submit scans for members outside the team associated with the scanned QR token.
5. **Real-time updates**: Verify `ScanRecord` is written immediately and subsequent scan check lists the member as `already_scanned=True`.

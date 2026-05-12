# Phase 8 Context: Room Configuration UI

## Overview
Replace the raw JSON textarea for room configuration with a dynamic, structured JavaScript-driven form that builds the JSON behind the scenes.

## Decisions Made

### 1. UI Approach
- **Decision:** Dynamic JavaScript form with "Add Room" / "Add Column" / remove buttons.
- **Rationale:** No-code experience for organizers. Vanilla JS, no framework needed.

### 2. Room Types
- **Decision:** Support both `configured` (bench columns) and `open` (auditorium seats) room types via a dropdown per room.
- **Rationale:** Matches the full capability of the seating algorithm in `services/seating.py`.

### 3. JSON Visibility
- **Decision:** Completely replace the JSON textarea. A hidden input holds the generated JSON.
- **Rationale:** The structured UI covers all options; no need for a raw editor.

## Code Context
- **Existing template:** `hackathon_detail.html` — seating section currently has a `RoomConfigForm` textarea.
- **Algorithm input format:**
  - Configured: `{"room_no": 1, "type": "configured", "columns": [{"bench_count": 5, "capacity": 2}]}`
  - Open: `{"room_no": 2, "type": "open", "total_seats": 50, "seats_per_row": 10}`
- **View:** `RunSeatingAllocationView` reads `room_configuration` from POST data — no backend changes needed, only the template/form.

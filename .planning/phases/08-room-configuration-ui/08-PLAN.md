---
wave: 1
depends_on: []
files_modified:
  - backend/organizer/templates/organizer/hackathon_detail.html
  - backend/organizer/views.py
  - backend/organizer/forms.py
autonomous: true
---

# Phase 8: Room Configuration UI

<must_haves>
- Dynamic JS form replacing the raw JSON textarea.
- "Add Room" button adds a new room card.
- Each room card has: room number input, room type dropdown (Configured / Open).
- Configured type: "Add Column" button, each column has bench_count + capacity inputs, remove button.
- Open type: total_seats + seats_per_row inputs.
- Remove room button per card.
- Hidden input holds the serialized JSON, populated on form submit.
- Pre-populates from existing hackathon.room_configuration if present.
- Form posts to existing RunSeatingAllocationView — no backend changes needed.
</must_haves>

<threat_model>
- Low: JavaScript disabled — form won't work. Acceptable for admin-facing tool.
- Medium: Invalid data entry (negative numbers, empty fields). Mitigated by HTML5 min/required attributes + JS validation on submit.
</threat_model>

<task>
<read_first>
- backend/organizer/templates/organizer/hackathon_detail.html
- backend/organizer/views.py (HackathonDetailView.get_context_data)
</read_first>
<action>
Replace the seating allocation section in hackathon_detail.html.

1. Remove the `{{ room_config_form.room_configuration }}` textarea rendering.
2. Add a `<div id="room-builder">` container.
3. Add an "Add Room" button that creates a new room card via JavaScript.
4. Each room card contains:
   - Room Number: `<input type="number" min="1" required>`
   - Room Type: `<select>` with options "configured" and "open"
   - **If configured:** A columns container with "Add Column" button. Each column has:
     - Bench Count: `<input type="number" min="1" value="1">`
     - Capacity per Bench: `<input type="number" min="1" value="2">`
     - Remove column button (×)
   - **If open:** 
     - Total Seats: `<input type="number" min="1">`
     - Seats per Row: `<input type="number" min="1" value="20">`
   - Remove room button (🗑)
5. Add a hidden input `<input type="hidden" name="room_configuration">`.
6. On form submit, JavaScript iterates all room cards, builds the JSON array, sets it as the hidden input value, then submits.
7. If `hackathon.room_configuration` exists, pre-populate the room cards on page load using an inline `<script>` that reads the JSON from a Django template variable.

Style the room cards to match the existing page design:
- Room cards: white background, border, rounded corners, margin-bottom.
- Column rows: flex layout with gap.
- Buttons: match existing .btn-primary / .btn-danger / .btn-secondary styles.
- Add subtle transitions on add/remove.
</action>
<acceptance_criteria>
- No raw JSON textarea visible.
- Can add/remove rooms dynamically.
- Room type switching shows/hides appropriate fields.
- Can add/remove columns within configured rooms.
- Form submits correct JSON to the existing endpoint.
- Pre-populates from existing room_configuration.
- "Run Allocation" button and CSV export link still work.
</acceptance_criteria>
</task>

<task>
<action>
Clean up backend: remove RoomConfigForm from forms.py and its usage from views.py since the UI now handles room config directly.

1. In `forms.py`: Remove the `RoomConfigForm` class.
2. In `views.py` `HackathonDetailView.get_context_data`: Remove `room_config_form` from context. Instead, pass `room_configuration_json` as a JSON string for the template's pre-population script.
</action>
<acceptance_criteria>
- RoomConfigForm deleted from forms.py.
- View passes raw JSON string instead of form instance.
- No import errors.
</acceptance_criteria>
</task>

<verification_criteria>
- `python manage.py check` passes.
- Hackathon detail page loads without errors.
- Room builder UI renders with add/remove functionality.
- Submitting the form correctly runs seating allocation.
- Existing room_configuration data pre-populates the UI.
</verification_criteria>

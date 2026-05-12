# Phase 4 Context

## Domain Boundary
Integrating the existing pure Python seating allocation algorithm into the Django `organizer` app. This allows hackathon organizers to generate, save, and view seating arrangements for registered teams based on room configurations directly through the Syntra API.

## Prior Decisions
- The project uses `Team` and `TeamMember` (guest records) in the `participant` app for gathering the team sizes and data.
- Identifiers and role-scoping follow the standard DRF token authentication established in Phase 1.

## Decisions
- **Persistence of Room Configuration:** Store as a `JSONField` on the `Hackathon` model. This is simple, highly flexible, and perfectly matches the expected frontend payload.
- **Persistence of Allocation Results:** Store as a `JSONField` on the `Hackathon` model. This explicitly locks the seating chart in place once generated, preventing changes if team sizes fluctuate slightly after the initial allocation.
- **Triggering the Allocation:** Handled via a Manual API Endpoint. Organizers explicitly call the endpoint (e.g., clicking "Generate Seating") giving them control over when to lock in the seating.
- **Output / Export Format:** The endpoint will provide JSON for the UI map. An additional endpoint (or query parameter) will be provided to download the raw allocation as a CSV export for volunteers to use on the day of the event.

## Deferred Ideas
- Tracking physical Check-In state of these allotted seats (belongs to the QR Attendance phase).
- Complex Django Models for `Room`, `Bench`, and `Seat` tracking.

## Canonical Refs
None explicitly referenced.

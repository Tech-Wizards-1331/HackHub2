# Architecture

## Pattern
The codebase follows a hybrid Django Architecture:
- **Traditional MVT:** Used for server-rendered pages via `frontend/templates`.
- **RESTful API:** Developed via Django REST Framework (`rest_framework`) for decoupled frontends or dynamic client-side interactions.

## Key Layers & Apps
- **`syntra`**: Core project application handling settings and root URL routing.
- **`accounts`**: Manages the custom user model, social authentication workflows, and profile interactions.
- **`organizer`**: Contains domain logic for hackathon organizers (creating hackathons, managing problem statements, tracking statuses).
- **`participant`**: Contains domain logic for hackathon participants (registrations, team management, profile dashboards).

## Data Flow
- User interactions originate either from the rendered templates or via REST API endpoints.
- Authentication relies on a mix of session auth (for server-rendered views) and JWT (for REST endpoints).
- The `accounts.User` model is the central entity, linked across all domains via ForeignKeys to manage roles and access control.
